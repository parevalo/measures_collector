import sqlite3
import numpy as np
import ee
import pandas as pd
import datetime
import geopandas

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
    band_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7',  'B6', 'pixel_qa']
    name_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'THERMAL',
                 'pixel_qa']
    return ee.Image(img).select(band_list).rename(name_list)


def stack_renamer_l8_C1(img):
    band_list = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'pixel_qa']
    name_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'THERMAL',
                 'pixel_qa']
    return ee.Image(img).select(band_list).rename(name_list)


# filter and merge collections
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


# Utility function for calculating spectral indices
def doIndices(fullImage):

    image = fullImage.select(['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2'])

    # Parameters
    cfThreshold = 20000
    soil = [2000, 3000, 3400, 5800, 6000, 5800]
    gv = [500, 900, 400, 6100, 3000, 1000]
    npv = [1400, 1700, 2200, 3000, 5500, 3000]
    shade = [0, 0, 0, 0, 0, 0]
    cloud = [9000, 9600, 8000, 7800, 7200, 6500]
    cfThreshold = ee.Image.constant(cfThreshold)

    #  Do spectral unmixing on a single image  */
    unmixImage = ee.Image(image).unmix([gv, shade, npv, soil, cloud], True,True).multiply(ee.Image(10000))\
                 .rename(['band_0', 'band_1', 'band_2','band_3','band_4'])
    newImage = ee.Image(fullImage).addBands(unmixImage)

    ndfi = ee.Image(unmixImage).expression(
      '((GV / (10000 - SHADE)) - (NPV + SOIL)) / ((GV / (10000 - SHADE)) + NPV + SOIL)', {
        'GV': ee.Image(unmixImage).select('band_0'),
        'SHADE': ee.Image(unmixImage).select('band_1'),
        'NPV': ee.Image(unmixImage).select('band_2'),
        'SOIL': ee.Image(unmixImage).select('band_3')
      })
    ndvi = ee.Image(image).normalizedDifference(['NIR','RED']).rename('NDVI')
    evi = ee.Image(image).expression(
          'float(2.5*(((B4/10000) - (B3/10000)) / ((B4/10000) + (6 * (B3/10000)) - (7.5 * (B1/10000)) + 1)))',
          {
              'B4': ee.Image(image).select(['NIR']),
              'B3': ee.Image(image).select(['RED']),
              'B1': ee.Image(image).select(['BLUE'])
          }).rename('EVI')

    return ee.Image(newImage)\
        .addBands([ndfi.rename(['NDFI']).multiply(10000), ndvi.multiply(10000), evi.multiply(10000)])\
        .select(['band_0','band_1','band_2','band_3','NDFI','NDVI','EVI','BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL','pixel_qa'])\
        .rename(['GV','Shade','NPV','Soil','NDFI','NDVI','EVI','BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL','pixel_qa'])\



def save_amazon(interface, Plot_interface):
    """ Save the sample to the database """

    idSample = 'N/A'
    lat =  'N/A'
    lon = 'N/A'
    num = 'N/A'
    lc1  = 'N/A'
    lc2 = 'N/A'
    lcConf = 'N/A'
    lcNotes = 'N/A'
    date1 = 'N/A'
    type1 = 'N/A'
    agent1 = 'N/A'
    conf1 = 'N/A'
    image1 = 'N/A'
    notes1 = 'N/A'
    date2 = 'N/A'
    type2 = 'N/A'
    agent2 = 'N/A'
    conf2 = 'N/A'
    image2 = 'N/A'
    notes2 = 'N/A'
    date3 = 'N/A'
    type3 = 'N/A'
    agent3 = 'N/A'
    conf3 = 'N/A'
    image3 = 'N/A'
    notes3 = 'N/A'

    lc1 = interface.drop2.value
    lc2 = interface.drop3.value
    num = interface.drop1.value
    lcConf = interface.confidence.value
    lcNotes = interface.notes1.value
    idSample = Plot_interface.current_id
    lat = Plot_interface.m.center[0]
    lon = Plot_interface.m.center[1]

    if interface.change_year1.value != 'Year':
        date1 = interface.change_year1.value
        type1 = interface.change_type1.value
        agent1 = interface.change_agent1.value
        conf1 = interface.change_conf1.value
        image1 = interface.change_image1.value
        notes1 = interface.change_notes1.value

    if interface.change_year2.value != 'Year':
        date2 = interface.change_year2.value
        type2 = interface.change_type2.value
        agent2 = interface.change_agent2.value
        conf2 = interface.change_conf2.value
        image2 = interface.change_image2.value
        notes2 = interface.change_notes2.value

    if interface.change_year3.value != 'Year':
        date3 = interface.change_year3.value
        type3 = interface.change_type3.value
        agent3 = interface.change_agent3.value
        conf3 = interface.change_conf3.value
        image3 = interface.change_image3.value
        notes3 = interface.change_notes3.value


    # Reset the buttons
    # Save to drive
    sampleInputList = [str(idSample), str(lat), str(lon), str(num), str(lc1), str(lc2), str(lcConf), str(lcNotes),
                       str(date1), str(type1), str(agent1), str(conf1), str(image1), str(notes1),
                       str(date2), str(type2), str(agent2), str(conf2), str(image2), str(notes2),
                       str(date3), str(type3), str(agent3), str(conf3), str(image3), str(notes3)]

    sampleInputListFull = sampleInputList

    interface.sheet.insert_row(sampleInputListFull, 2)

    # Change save validity state
    interface.valid.value = True
    interface.valid.description='Saved!'

    interface.reset_widgets()


# Old: save sample to database
def save_sample(interface, Plot_interface):
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
    coverType = interface.drop0.value
    changeAgent = interface.change_selector.value
    changeAgent = [str(i) for i in changeAgent]
    changeAgent = ', '.join(changeAgent)
    if changeAgent != 'None':
        confCA = interface.ca_confidence.value
        break_year = interface.break_year.value
        break_range1 = interface.break_years.value[0]
        break_range2 = interface.break_years.value[1]
    else:
        confCA = 'N/A'
        break_year = 'N/A'
        break_range1 = 'N/A'
        break_range2 = 'N/A'
    ca_other = interface.change_other.value
    if ca_other == 'Specify other':
        ca_other = 'N/A'

    direction = interface.direction.value
    direction = [str(i) for i in direction]
    direction = ', '.join(direction)

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
            vegType1 = interface.veg_selector.value
            vegType1 = [str(i) for i in vegType1]
            vegType1 = ', '.join(vegType1)
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

    sampleInput = (idSample, lat, lon, year1, year2, direction, coverType, condition,
                       changeAgent, ca_other, confCA, class1, waterType,
                       bareType, albedo, use, height, transport, impervious, density,
                       vegType1, herbaceousType, shrubType, forestPhenology, leafType,
                       location, conf, notes_value, break_year, break_range1, break_range2)


    # Put sample information into database
    c.execute("""insert into measures
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
    sampleInputList = [str(idSample), str(lat), str(lon), str(year1), str(year2), direction, coverType, condition,
                       changeAgent, ca_other, confCA, class1, waterType,
                       bareType, albedo, use, height, transport, impervious, density,
                       vegType1, herbaceousType, shrubType, forestPhenology, leafType, location, conf, notes_value]

    sampleInputListFull = sampleInputList

    interface.sheet.insert_row(sampleInputListFull, 2)

   # Save break information to second sheet
    if condition == 'Break':
        breakList = [str(idSample), str(lat), str(lon), changeAgent, ca_other, confCA, break_year, break_range1, break_range2]
        interface.sheet2.insert_row(breakList, 2)

# Calculate spectral indices
def get_indices(df):

    df['BRIGHTNESS'] = (df['BLUE'] * 0.2043) + (df['GREEN'] * 0.4158) + (df['RED'] * 0.5524) +\
                       (df['NIR'] * 0.5741) + (df['SWIR1'] * 0.3124) + (df['SWIR2'] * 0.2303)
    df['GREENNESS'] = (df['BLUE'] * -0.1603) + (df['GREEN'] * 0.2819) + (df['RED'] * -0.4934) +\
                      (df['NIR'] * 0.7940) + (df['SWIR1'] * -0.0002) + (df['SWIR2'] * -0.1446)
    df['WETNESS'] = (df['BLUE'] * 0.0315) + (df['GREEN'] * 0.2021) + (df['RED'] * 0.3102) +\
                    (df['NIR'] * 0.1594) + (df['SWIR1'] * -0.6806) + (df['SWIR2'] * -0.6109)

    return df

# Get time series for location as a pandas dataframe
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
    data = data[['id', 'datetime', 'ord_time', 'BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1',
                'SWIR2', 'THERMAL', 'pixel_qa', 'doy', 'color']]
    data = data.dropna()
    data = get_indices(data)
    return data

# make color list for all 365 days of year
def get_color_list():

    colors = [['#000000'] * 79 \
             + ['#41b6c4'] * 93 \
             + ['#41ab5d'] * 94 \
             + ['#e31a1c'] * 89 \
             + ['#000000'] * 11][0]

    return colors


# Get the URL for an earth engine image. TODO: Wrong file
def GetTileLayerUrl(ee_image_object):

    map_id = ee.Image(ee_image_object).getMapId()
    tile_url_template = "https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}"
    return tile_url_template.format(**map_id)


# Old
# Convert a FeatureCollection into a pandas DataFrame
# Features is a list of dict with the output
def fc2df(fc):

    features = fc.getInfo()['features']
    dictarr = []
    for f in features:
        # Store all attributes in a dict
        attr = f['properties']
        dictarr.append(attr)

    return pd.DataFrame(dictarr)

# Old
# Get time series for a location as a pandas dataframe
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

# Old (no longer used)
# Get time series for location in format to use in pyccd
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

# Append two dataframes
def update_df(df, df2):

    df = df.append(df2)
    return df


# Convert a FeatureCollection into a geopandas DataFrame
# Features is a list of dict with the output
def fc2dfgeo(fc):

    features = ee.FeatureCollection(fc).getInfo()['features']

    dictarr = []

    for f in features:
        # Store all attributes in a dict
        attr = f['properties']
        # and treat geometry separately
        attr['geometry'] = f['geometry']
        dictarr.append(attr)

    df = geopandas.GeoDataFrame(dictarr)
    return df

# Check if there's an ID field, if not assign index
def check_id(fc_df):

    if 'ID' not in fc_df.columns:
        first_index = fc_df.index.min()
        fc_df['ID'] = fc_df.index
    else:
        first_index = fc_df['ID'].min()
    fc_df = fc_df.set_index('ID')

    return fc_df, first_index

# Plot TS from clicked point
def handle_draw(action, geo_json, current_band, year_range, doy_range):

    # Get the selected coordinates from the map's drawing control.
    coords = geo_json['geometry']['coordinates']
    click_col = get_full_collection(coords, year_range, doy_range)
    click_df = get_df_full(click_col, coords)

    return click_col, click_df


# Calculate 90m bbox around clicked point for opportunistic
# training data collection
def calculate_clicked_bbox(geojson):
    click_geom = ee.Geometry(geojson['geometry'])
    # Asset with projection info per zone
    all_zones = ee.FeatureCollection("users/parevalo_bu/measures/measures_zones_crs")
    zone = all_zones.filterBounds(click_geom).first()
    target_proj = zone.get("CRS")
    bbox = click_geom.buffer(45, 0, target_proj).bounds(0.01, target_proj)
    return bbox
