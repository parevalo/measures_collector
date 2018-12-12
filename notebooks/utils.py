import sqlite3
import ee
import pandas as pd
import datetime

# Filter collection by point and date
def collection_filtering(point, collection_name, year_range, doy_range):
    collection = ee.ImageCollection(collection_name)\
    .filterBounds(point)\
    .filter(ee.Filter.calendarRange(year_range[0], year_range[1], 'year'))\
    .filter(ee.Filter.dayOfYear(doy_range[0],doy_range[1]))
    return collection


# Cloud masking for C1, L4-L7. Operators capitalized to
# avoid confusing with internal Python operators
def cloud_mask_l4_7_C1(img):
    pqa = ee.Image(img).select(['pixel_qa'])
    mask = (pqa.eq(66)).Or(pqa.eq(130))\
    .Or(pqa.eq(68)).Or(pqa.eq(132))
    return ee.Image(img).updateMask(mask)

# Cloud masking for C1, L8
def cloud_mask_l8_C1(img):
    pqa = ee.Image(img).select(['pixel_qa'])
    mask = (pqa.eq(322)).Or(pqa.eq(386)).Or(pqa.eq(324))\
    .Or(pqa.eq(388)).Or(pqa.eq(836)).Or(pqa.eq(900))
    return ee.Image(img).updateMask(mask)

def stack_renamer_l4_7_C1(img):
     band_list = ['B1', 'B2','B3','B4','B5','B7', 'B6','pixel_qa']
     name_list = ['BLUE','GREEN','RED','NIR','SWIR1','SWIR2','THERMAL','pixel_qa']
     return ee.Image(img).select(band_list).rename(name_list)

def stack_renamer_l8_C1(img):
     band_list = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10','pixel_qa'];
     name_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL','pixel_qa'];
     return ee.Image(img).select(band_list).rename(name_list);

#filter and merge collections
def get_full_collection(coords, year_range, doy_range):
    point = ee.Geometry.Point(coords)
    l8_renamed = collection_filtering(point, 'LANDSAT/LC08/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l8_C1)
    l8_filtered1 = l8_renamed.map(cloud_mask_l8_C1)

    l7_renamed = collection_filtering(point, 'LANDSAT/LE07/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l4_7_C1);
    l7_filtered1 = l7_renamed.map(cloud_mask_l4_7_C1)

    l5_renamed = collection_filtering(point, 'LANDSAT/LT05/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l4_7_C1)
    l5_filtered1 = l5_renamed.map(cloud_mask_l4_7_C1)


    all_scenes = ee.ImageCollection((l8_filtered1.merge(l7_filtered1)).merge(l5_filtered1)).sort('system:time_start')
    return all_scenes

def save_sample(interface, Plot_interface):
    """ Save the sample to the database """
    # TODO: This should be backed up somehow

    # Connect to the database
    conn = sqlite3.connect(interface.dbPath)
    c = conn.cursor()

    # Get everything in right format
    year1 = interface.years.value[0]
    year2 = interface.years.value[1]

    waterType = 'N/A'
    bareType = 'N/A'
    albedo = 'N/A'
    use = 'N/A'
    height = 'N/A'
    transport = 'N/A'
    impervious = 'N/A'
    density = 'N/A'
    vegType1 = 'N/A'
    herbaceousType = 'N/A'
    shrubType = 'N/A'
    forestPhenology = 'N/A'
    leafType = 'N/A'
    location = 'N/A'

    condition = interface.drop9.value
    changeAgent = interface.change_selector.value
    changeAgent = [str(i) for i in changeAgent]
    changeAgent = ', '.join(changeAgent)

    class1 = 'Unfilled'

    # Ice/Snow
    if interface.drop1.value == 'Yes':
        class1 = 'Snow/Ice'
    else:
        if interface.drop2.value == 'No': #Non-Veg
            class1 = interface.drop3.value
            if class1 == 'Water':
                waterType = interface.drop4.value
            elif class1 == 'Bare':
                bareType = interface.drop4.value
            else:
                albedo = interface.drop4.value #HERE
                use = interface.drop5.value
                height = interface.drop6.value
                transport = interface.drop7.value
                impervious = interface.drop8.value
        elif interface.drop2.value == 'Yes': #Veg
            density = interface.drop3.value
            if interface.drop5.value == 'No': #Herbaceous
                class1 = 'Herbaceous'
                herbaceousType = interface.drop6.value
            elif interface.drop5.value == 'Yes':
                class1 = 'Forest'
                forestPhenology = interface.drop6.value
                leafType = interface.drop7.value
                location = interface.drop8.value

    conf = interface.confidence.value
    notes_value = interface.notes.value
    idSample = Plot_interface.current_id
    lat = Plot_interface.m.center[0]
    lon = Plot_interface.m.center[1]

    sampleInput = (idSample, lat, lon, year1, year2, condition,
                   changeAgent, class1, waterType, bareType, albedo,
                   use, height, transport, impervious, density,
                   vegType1, herbaceousType, shrubType, forestPhenology,
                   leafType, location, conf, notes_value)

    # Put sample information into database
    c.execute("""insert into sample4
              values {i}""".format(i=sampleInput))

    # Save (commit) the changes
    conn.commit()

    # Close the cursor
    c.close()

    # Change save validity state
    interface.valid.value = True
    interface.valid.description='Saved!'

    # Reset the buttons
    interface.years.set_trait('value',[2012, 2015])

    # Save to drive
    sampleInputList = [str(idSample), str(lat), str(lon), str(year1), str(year2), condition, changeAgent, class1, waterType,
                       bareType, albedo, use, height, transport, impervious, density,
                       vegType1, herbaceousType, shrubType, forestPhenology, leafType, location, conf, notes_value]
    interface.sheet.insert_row(sampleInputList, 2)

def get_df_full(collection, coords):
    point = ee.Geometry.Point(coords)
    # Sample for a time series of values at the point.
    geom_values = collection.filterBounds(point).getRegion(geometry=point, scale=30)
    geom_values_list = ee.List(geom_values).getInfo()
    # Convert to a Pandas DataFrame.
    header = geom_values_list[0]
    data = pd.DataFrame(geom_values_list[1:], columns=header)
    data['datetime'] = pd.to_datetime(data['time'], unit='ms', utc=True)
    data['doy'] = pd.DatetimeIndex(data['datetime']).dayofyear
    color_list = get_color_list()
    data['color'] = [color_list[i] for i in data['doy']]
    data.set_index('time')
    data = data.sort_values('datetime')
    data['ord_time'] = data['datetime'].apply(datetime.date.toordinal)
    data = data[['id', 'datetime', 'ord_time', 'BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'THERMAL', 'pixel_qa', 'doy', 'color']]
    return data

def get_color_list():
    colors = [['#000000'] * 79 \
             + ['#41b6c4'] * 93 \
             + ['#41ab5d'] * 94 \
             + ['#e31a1c'] * 89 \
             + ['#000000'] * 11][0]

    return colors


def GetTileLayerUrl(ee_image_object):
    map_id = ee.Image(ee_image_object).getMapId()
    tile_url_template = "https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}"
    return tile_url_template.format(**map_id)


# Old
def fc2df(fc):
    # Convert a FeatureCollection into a pandas DataFrame
    # Features is a list of dict with the output
    features = fc.getInfo()['features']
    dictarr = []
    for f in features:
        # Store all attributes in a dict
        attr = f['properties']
        dictarr.append(attr)

    return pd.DataFrame(dictarr)

# Calculate period statistics, seems to work but it's so ugly!
def calc_period_stats(yr_list, collection, reducer, stat_name, bands):
    def auxfnc(year):
        start = ee.Date(year)
        end = start.advance(step, 'year').advance(-1, 'day')

        return collection\
        .select(bands)\
        .filterDate(start, end)\
        .reduce(reducer)\
        .set({'system:time_start': start, 'system:time_end': end, 'statistic': stat_name})
    period_stats = yr_list.map(auxfnc)
    return period_stats


def get_df(collection, coords, band):
    point = ee.Geometry.Point(coords)
    # Sample for a time series of values at the point.
    geom_values = collection.filterBounds(point).select(band).getRegion(geometry=point, scale=30)
    geom_values_list = ee.List(geom_values).getInfo()
    # Convert to a Pandas DataFrame.
    header = geom_values_list[0]
    data = pd.DataFrame(geom_values_list[1:], columns=header)
    data['datetime'] = pd.to_datetime(data['time'], unit='ms', utc=True)
    data.set_index('time')
    data = data.sort_values('datetime')
    data = data[['id', 'datetime', band]]
    return data

def make_df_pyccd(collection, point):
    band_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL', 'pixel_qa']
    rename_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL', 'pixel_qa']
    info = collection.getRegion(point, 30).getInfo()
    header = info[0]
    data = np.array(info[1:])
    iTime = header.index('time')
    time = [datetime.datetime.fromtimestamp(i/1000) for i in (data[0:,iTime].astype(int))]
    time_new = [t.toordinal() for t in (time)]
    iBands = [header.index(b) for b in band_list]
    yData = data[0:,iBands].astype(np.float)
    df = pd.DataFrame(data=yData, index=list(range(len(yData[:,0]))), columns=rename_list)
    df['time'] = time_new
    return df

def update_df(df, df2):
    df = df.append(df2)
    return df

