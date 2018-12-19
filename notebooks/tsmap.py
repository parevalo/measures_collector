from ipywidgets import Button, HBox, VBox, Label, BoundedIntText, HTML, Dropdown, Layout, FloatText
import datetime
import dateutil.parser
import pandas as pd
import ee
import pprint
import ipywidgets
import ipywidgets as widgets
import IPython.display
import numpy as np
import traitlets
import ipyleaflet
from dateutil import parser
import geopandas
import sqlite3
import ccd
import os
import qgrid
import bqplot

# Google sheets API
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from utils import get_full_collection, get_df_full, GetTileLayerUrl



class Plot_interface(object):
    """Class to handle map and plot interaction"""

    # Declare class attributes
    pyccd_flag = False
    pyccd_flag2 = False
    current_band = ''
    band_index1 = 4
    band_index2 = 4
    click_col = ''
    point_color = ['#43a2ca']
    click_df = pd.DataFrame()
    sample_col = ''
    sample_df = pd.DataFrame()
    PyCCDdf = pd.DataFrame()
    table = pd.DataFrame()
    band_list =['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2']
    year_range = [ 1986, 2018 ]
    doy_range = [ 1, 365 ]
    step = 1 #in years

    # Create widget controls
    next_pt = Button(value=False, description='Next point', disabled=False)
    previous_pt = Button(value=False, description='Previous point', disabled=False)
    pyccd_button = Button(value=False, description='Run PyCCD 1', disabled=False)
    pyccd_button2 = Button(value=False, description='Run PyCCD 2', disabled=False)
    band_selector1 = Dropdown(options=['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2'],
                             description='Select band', value=None)
    band_selector2 = Dropdown(options=['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2'],
                             description='Select band', value=None)
    image_band_1 = Dropdown(options=['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2'],
                             description='Red:', value='SWIR1')
    image_band_2 = Dropdown(options=['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2'],
                         description='Green:', value='NIR')
    image_band_3 = Dropdown(options=['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2'],
                             description='Blue:', value='RED')
    stretch_min = FloatText(value=0, description='Min:', disabled=False)
    stretch_max = FloatText(value=6000, description='Min:', disabled=False)

    # Clear layers on map
    clear_layers = Button(value=False, description='Clear Map', disabled=False)

    # Color points by DOY
    color_check = widgets.Checkbox(
                    value=False,
                    description='Color DOY',
                    disabled=False
    )

    idBox = widgets.Text(
                value='0',
                description='ID:',
                disabled=False
            )

    ylim = widgets.IntRangeSlider(value=[0, 4000], min=0, max=10000,
            step=500, description='YLim:', disabled=False, continuous_update=False,
            orientation='horizontal', readout=True, readout_format='d')

    xlim = widgets.IntRangeSlider(value=[2000, 2018], min=1986, max=2018,
            step=1, description='XLim:', disabled=False, continuous_update=False,
            orientation='horizontal', readout=True, readout_format='d')

    ylim2 = widgets.IntRangeSlider(value=[0, 4000], min=0, max=10000,
            step=500, description='YLim:', disabled=False, continuous_update=False,
            orientation='horizontal', readout=True, readout_format='d')

    xlim2 = widgets.IntRangeSlider(value=[2000, 2018], min=1986, max=2018,
            step=1, description='XLim:', disabled=False, continuous_update=False,
            orientation='horizontal', readout=True, readout_format='d')


    coords_label = Label()
    pt_message = HTML("Current ID: ")
    time_label = HTML(value='')
    selected_label = HTML("ID of selected point")
    hover_label = HTML("test value")
    text_brush = HTML(value = 'Selected year range:')
    kml_link = HTML(value = 'KML:')
    error_label = HTML(value = 'Load a point')


    # Create map including streets and satellite and controls
    m = ipyleaflet.Map(zoom=5, layout={'height':'400px'},
                       center=(3.3890701010382958, -67.32297252983098),dragging=True,
                       close_popup_on_click=False, basemap=ipyleaflet.basemaps.Esri.WorldStreetMap)

    streets = ipyleaflet.basemap_to_tiles(ipyleaflet.basemaps.Esri.WorldImagery)
    m.add_layer(streets)

    dc = ipyleaflet.DrawControl(marker={'shapeOptions': {'color': '#ff0000'}},
                                polygon={}, circle={}, circlemarker={}, polyline={})


    # Table widget
    table_widget = qgrid.show_grid(table, show_toolbar=False)

    # Set plots
    # Plot scales. HERE
    lc1_x = bqplot.DateScale(min=datetime.date(xlim.value[0], 2, 1), max=datetime.date(xlim.value[1], 1, 1))

    # DOY scale
    lc1_x3 = bqplot.LinearScale(min=0, max=365)

    lc2_y = bqplot.LinearScale(min=ylim.value[0], max=ylim.value[1])

    lc1_x2 = bqplot.DateScale(min=datetime.date(xlim.value[0], 2, 1), max=datetime.date(xlim.value[1], 1, 1))
    lc2_y2 = bqplot.LinearScale(min=ylim.value[0], max=ylim.value[1])

    # Main scatter plot for samples
    lc2 = bqplot.Scatter(
        x=[],
        y=[],
        scales={'x': lc1_x, 'y': lc2_y},
        size=[1,1],
        interactions={'click': 'select', 'hover': 'tooltip'},
        selected_style={'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
        unselected_style={'opacity': 0.5},
        display_legend=True,
        labels = ['Sample point']
    )

    # Pyccd model fit
    lc4 = bqplot.Lines(
        x=[],
        y=[],
        colors=['black'],
        stroke_width=3,
        scales={'x': lc1_x, 'y': lc2_y},
        size=[1,1],
    )

    # Pyccd model break
    lc5 = bqplot.Scatter(
        x=[],
        y=[],
        marker='triangle-up',
        colors=['red'],
        scales={'x': lc1_x, 'y': lc2_y},
        size=[1,1],
        display_legend=False,
        labels = ['Model Endpoint']
    )

    # Scatter plot for clicked points in map
    lc3 = bqplot.Scatter(
        x=[],
        y=[],
        scales={'x': lc1_x2, 'y': lc2_y2},
        size=[1,1],
        colors=['gray'],
        interactions={'click': 'select', 'hover': 'tooltip'},
        selected_style={'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
        unselected_style={'opacity': 0.5},
        display_legend=True,
        labels = ['Clicked point']
    )

    # Pyccd model fit for clicked point
    lc6 = bqplot.Lines(
        x=[],
        y=[],
        colors=['black'],
        stroke_width=3,
        scales={'x': lc1_x2, 'y': lc2_y2},
        size=[1,1],
    )

    # Pyccd model break for clicked point
    lc7 = bqplot.Scatter(
        x=[],
        y=[],
        marker='triangle-up',
        colors=['red'],
        scales={'x': lc1_x2, 'y': lc2_y2},
        size=[1,1],
        display_legend=False,
        labels = ['Model Endpoint']
    )

    # Scatter for sample DOY
    lc8 = bqplot.Scatter(
        x=[],
        y=[],
        scales={'x': lc1_x3, 'y': lc2_y},
        size=[1,1],
        interactions={'click': 'select', 'hover': 'tooltip'},
        selected_style={'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
        unselected_style={'opacity': 0.5},
        display_legend=True,
        labels = ['Sample point']
    )

    # Plot axes.
    x_ax1 = bqplot.Axis(label='Date', scale=lc1_x, num_ticks = 6, tick_format='%Y')
    x_ax2 = bqplot.Axis(label='Date', scale=lc1_x2, num_ticks = 6, tick_format='%Y')
    x_ax3 = bqplot.Axis(label='DOY', scale=lc1_x3, num_ticks = 6)

    x_ay1 = bqplot.Axis(label='SWIR1', scale=lc2_y, orientation='vertical')
    x_ay2 = bqplot.Axis(label='SWIR1', scale=lc2_y2, orientation='vertical')


    # Create a figure for sample points.
    fig = bqplot.Figure(
        marks=[lc2, lc4, lc5],
        axes=[x_ax1, x_ay1],
        layout={'height':'300px', 'width':'100%'},
        title="Sample TS"
    )

    # Create a figure for clicked points.
    fig2 = bqplot.Figure(
        marks=[lc3, lc6, lc7],
        axes=[x_ax2, x_ay2],
        layout={'height':'300px', 'width':'100%'},
        title="Clicked TS"
    )

    # Create a figure for sample DOY.
    fig3 = bqplot.Figure(
        marks=[lc8],
        axes=[x_ax3, x_ay1],
        layout={'height':'300px', 'width':'100%'},
        title="Clicked TS"
    )

    def __init__(self, navigate):
        Plot_interface.navigate = navigate
        Plot_interface.band_index1 = 4
        Plot_interface.band_index2 = 4
        Plot_interface.pyccd_flag = False
        Plot_interface.pyccd_flag2 = False
        Plot_interface.table = None
        # Set up database
        conn = sqlite3.connect(Plot_interface.navigate.dbPath)
        Plot_interface.current_id = Plot_interface.navigate.current_id
        Plot_interface.c = conn.cursor()
        Plot_interface.minv = 0
        Plot_interface.maxv = 6000
        Plot_interface.b1 = 'SWIR1'
        Plot_interface.b2 = 'NIR'
        Plot_interface.b3 = 'RED'

    @classmethod
    def map_point(self):
        gjson = ipyleaflet.GeoJSON(data=Plot_interface.navigate.fc_df['geometry'][Plot_interface.current_id], name="Sample point")
        Plot_interface.m.center = gjson.data['coordinates'][::-1]
        Plot_interface.m.zoom = 12
        Plot_interface.m.add_layer(gjson)
        kmlstr = ee.FeatureCollection(ee.Geometry.Point(Plot_interface.navigate.fc_df['geometry'][Plot_interface.current_id]['coordinates'])).getDownloadURL("kml")
        Plot_interface.kml_link.value = "<a '_blank' rel='noopener noreferrer' href={}>KML Link</a>".format(kmlstr)

    @classmethod
    def get_ts(self):
        #try:
        Plot_interface.error_label.value = 'Loading'
        Plot_interface.current_band = Plot_interface.band_list[Plot_interface.band_index1]
        Plot_interface.sample_col = get_full_collection(Plot_interface.navigate.fc_df['geometry'][Plot_interface.current_id]['coordinates'],
                                                         Plot_interface.year_range, Plot_interface.doy_range)
        Plot_interface.sample_df = get_df_full(Plot_interface.sample_col, Plot_interface.navigate.fc_df['geometry'][Plot_interface.current_id]['coordinates']).dropna()
        Plot_interface.error_label.value = 'Point loaded!'
        #except:
        #    Plot_interface.error_label.value = 'Point could not be loaded!'

    def clear_map(b):
        Plot_interface.m.clear_layers()
        Plot_interface.m.add_layer(Plot_interface.streets)
        Plot_interface.map_point()


    @classmethod
    def plot_ts(self):
        current_band = Plot_interface.band_list[Plot_interface.band_index1]
        Plot_interface.lc2.x = Plot_interface.sample_df['datetime']
        if Plot_interface.color_check.value == False:
            Plot_interface.lc2.colors = list(Plot_interface.point_color)
            Plot_interface.lc8.colors = list(Plot_interface.point_color)
        else:
            Plot_interface.lc2.colors = list(Plot_interface.sample_df['color'].values)
            Plot_interface.lc8.colors = list(Plot_interface.sample_df['color'].values)
        Plot_interface.lc2.y = Plot_interface.sample_df[current_band]
        Plot_interface.x_ay1.label = current_band
        Plot_interface.lc4.x = []
        Plot_interface.lc4.y = []
        Plot_interface.lc5.x = []
        Plot_interface.lc5.y = []

        Plot_interface.lc8.x = Plot_interface.sample_df['doy']
        Plot_interface.lc8.y = Plot_interface.sample_df[current_band]

        #if pyccd_flag:
        if Plot_interface.pyccd_flag:
            Plot_interface.run_pyccd(0)

    # Go back or forth between sample points
    def advance(b):
        # Plot point in map
        Plot_interface.lc4.x = []
        Plot_interface.lc4.y = []
        Plot_interface.lc5.x = []
        Plot_interface.lc5.y = []
        Plot_interface.lc5.display_legend=False
        Plot_interface.pyccd_flag = False
        Plot_interface.current_id += 1
        Plot_interface.pt_message.value = "Point ID: {}".format(Plot_interface.current_id)
        Plot_interface.map_point()
        Plot_interface.get_ts()
        Plot_interface.plot_ts()
        Plot_interface.change_table(0)
        Plot_interface.navigate.valid.value = False
        Plot_interface.navigate.description='Not Saved'

    def decrease(b):
        # Plot point in map
        Plot_interface.lc4.x = []
        Plot_interface.lc4.y = []
        Plot_interface.lc5.x = []
        Plot_interface.lc5.y = []
        Plot_interface.lc5.display_legend=False
        Plot_interface.pyccd_flag = False
        Plot_interface.current_id -= 1
        Plot_interface.pt_message.value = "Point ID: {}".format(Plot_interface.current_id)
        Plot_interface.map_point()
        Plot_interface.get_ts()
        Plot_interface.plot_ts()
        Plot_interface.change_table(0)
        Plot_interface.navigate.valid.value = False
        Plot_interface.navigate.description='Not Saved'

    def change_table(b):
        # Update the table based on current ID

        # Get header
        cursor = Plot_interface.c.execute('select * from measures')
        names = list(map(lambda x: x[0], cursor.description))
        previous_inputs = pd.DataFrame()
        for i, row in enumerate(Plot_interface.c.execute("SELECT * FROM measures WHERE id = '%s'" % Plot_interface.current_id)):
            previous_inputs[i] = row
        previous_inputs = previous_inputs.T
        if previous_inputs.shape[0] > 0:
            previous_inputs.columns = names
        Plot_interface.table_widget.df = previous_inputs

    # Functions for changing image stretch
    def change_image_band1(change):
        new_band = change['new']
        Plot_interface.b1 = new_band
    def change_image_band2(change):
        new_band = change['new']
        Plot_interface.b2 = new_band
    def change_image_band3(change):
        new_band = change['new']
        Plot_interface.b3 = new_band

    # Band selection for sample point
    def on_band_selection1(change):
        new_band = change['new']
        #global band_index
        band_index = change['owner'].index
        Plot_interface.band_index1 = band_index
        Plot_interface.plot_ts()

    # Band selection for clicked point
    def on_band_selection2(change):
        new_band = change['new']
        band_index = change['owner'].index
        Plot_interface.band_index2 = band_index
        Plot_interface.lc3.x = Plot_interface.click_df['datetime']
        Plot_interface.lc3.y = Plot_interface.click_df[new_band]
        Plot_interface.x_ay2.label = new_band
        if Plot_interface.pyccd_flag2:
            Plot_interface.run_pyccd2(0)

    def change_yaxis(value):
        Plot_interface.lc2_y.min = Plot_interface.ylim.value[0]
        Plot_interface.lc2_y.max = Plot_interface.ylim.value[1]

    def change_xaxis(value):
        Plot_interface.lc1_x.min = datetime.date(Plot_interface.xlim.value[0], 2, 1)
        Plot_interface.lc1_x.max = datetime.date(Plot_interface.xlim.value[1], 2, 1)
        Plot_interface.year_range = [Plot_interface.xlim.value[0], Plot_interface.xlim.value[1]]

    def change_yaxis2(value):
        Plot_interface.lc2_y2.min = Plot_interface.ylim2.value[0]
        Plot_interface.lc2_y2.max = Plot_interface.ylim2.value[1]

    def change_xaxis2(value):
        Plot_interface.lc1_x2.min = datetime.date(Plot_interface.xlim2.value[0], 2, 1)
        Plot_interface.lc1_x2.max = datetime.date(Plot_interface.xlim2.value[1], 2, 1)


    def hover_event(self, target):
        Plot_interface.hover_label.value = str(target['data']['x'])

    # Add layer from clicked point in sample TS figure
    def click_event(self, target):
        pt_index = target['data']['index']
        current_band = Plot_interface.band_list[Plot_interface.band_index1]
        image_id = Plot_interface.sample_df['id'].values[pt_index]
        selected_image = ee.Image(Plot_interface.sample_col.filterMetadata('system:index', 'equals', image_id).first())
        tile_url = GetTileLayerUrl(selected_image.visualize(min=Plot_interface.stretch_min.value,
                                                            max=Plot_interface.stretch_max.value,
                                                            bands= [Plot_interface.b1, Plot_interface.b2,
                                                                    Plot_interface.b3]))

        Plot_interface.m.add_layer(ipyleaflet.TileLayer(url=tile_url, name=image_id))

    # Add layer from clicked point in clicked TS figure
    def click_event2(self, target):
        pt_index = target['data']['index']
        current_band = Plot_interface.band_list[Plot_interface.band_index2]
        #Find clicked image. .values needed to access the nth element of that list instead of indexing by ID
        image_id = Plot_interface.click_df['id'].values[pt_index]
        selected_image = ee.Image(Plot_interface.click_col.filterMetadata('system:index', 'equals', image_id).first())
        tile_url = GetTileLayerUrl(selected_image.visualize(min=Plot_interface.minv,
                                                            max=Plot_interface.maxv,
                                                            bands= [Plot_interface.b1, Plot_interface.b2,
                                                                    Plot_interface.b3]))

        Plot_interface.m.add_layer(ipyleaflet.TileLayer(url=tile_url, name=image_id))

    # Plot TS from clicked point
    def handle_draw(self, action, geo_json):
        # Get the selected coordinates from the map's drawing control.
        current_band = Plot_interface.band_list[Plot_interface.band_index2]
        coords = geo_json['geometry']['coordinates']
        Plot_interface.click_col = get_full_collection(coords, Plot_interface.year_range, Plot_interface.doy_range)
        Plot_interface.click_df = get_df_full(Plot_interface.click_col, coords).dropna()
        Plot_interface.lc6.x = []
        Plot_interface.lc6.y = []
        Plot_interface.lc7.x = []
        Plot_interface.lc7.y = []
        Plot_interface.lc3.x = Plot_interface.click_df['datetime']
        Plot_interface.lc3.y = Plot_interface.click_df[current_band]

        if Plot_interface.color_check.value == False:
            Plot_interface.lc3.colors = list(Plot_interface.point_color)
        else:
            Plot_interface.lc3.colors = list(Plot_interface.click_df['color'].values)

    # Plotting pyccd
    def plot_pyccd(results, band, plotband, dates, yl, ylabel, ts_type):
        mask = np.array(results['processing_mask']).astype(np.bool_)
        predicted_values = []
        prediction_dates = []
        break_dates = []
        start_dates = []

        for num, result in enumerate(results['change_models']):
            days = np.arange(result['start_day'], result['end_day'] + 1)
            prediction_dates.append(days)
            break_dates.append(result['break_day'])
            start_dates.append(result['start_day'])
            intercept = result[list(result.keys())[6+band]]['intercept']
            coef = result[list(result.keys())[6+band]]['coefficients']

            predicted_values.append(intercept + coef[0] * days +
                                    coef[1]*np.cos(days*1*2*np.pi/365.25) + coef[2]*np.sin(days*1*2*np.pi/365.25) +
                                    coef[3]*np.cos(days*2*2*np.pi/365.25) + coef[4]*np.sin(days*2*2*np.pi/365.25) +
                                    coef[5]*np.cos(days*3*2*np.pi/365.25) + coef[6]*np.sin(days*3*2*np.pi/365.25))

        num_breaks = len(break_dates)

        break_y = [plotband[dates == i][0] for i in break_dates]

        #break_y = [0] * num_breaks
        break_dates_plot = [datetime.datetime.fromordinal(i).strftime('%Y-%m-%d %H:%M:%S.%f') for i in break_dates]

        plot_dates = np.array([datetime.datetime.fromordinal(i) for i in (dates)])

        # Predicted curves
        all_dates = []
        all_preds = []
        for _preddate, _predvalue in zip(prediction_dates, predicted_values):
            all_dates.append(_preddate)
            all_preds.append(_predvalue)

        all_preds = [item for sublist in all_preds for item in sublist]
        all_dates = [item for sublist in all_dates for item in sublist]

        date_ord = [datetime.datetime.fromordinal(i).strftime('%Y-%m-%d %H:%M:%S.%f') for i in all_dates]
        _x = np.array(date_ord, dtype='datetime64')
        _y = all_preds

        if ts_type == 'sample_ts':
            Plot_interface.lc4.x = _x
            Plot_interface.lc4.y = _y
            Plot_interface.lc5.x = np.array(break_dates_plot, dtype='datetime64')
            Plot_interface.lc5.y = break_y
        elif ts_type == 'clicked_ts':
            Plot_interface.lc6.x = _x
            Plot_interface.lc6.y = _y
            Plot_interface.lc7.x = np.array(break_dates_plot, dtype='datetime64')
            Plot_interface.lc7.y = break_y

    # Go to a specific sample
    def go_to_sample(b):
        # Plot point in map
        Plot_interface.lc4.x = []
        Plot_interface.lc4.y = []
        Plot_interface.lc5.x = []
        Plot_interface.lc5.y = []
        Plot_interface.lc5.display_legend=False
        Plot_interface.pyccd_flag = False
        Plot_interface.current_id = int(b.value)
        Plot_interface.pt_message.value = "Point ID: {}".format(Plot_interface.current_id)
        Plot_interface.navigate.valid.value = False
        Plot_interface.navigate.description='Not Saved'
        Plot_interface.map_point()
        Plot_interface.get_ts()
        Plot_interface.plot_ts()

    # Run pyccd
    def run_pyccd(b):
        # Run pyCCD on current point
        Plot_interface.pyccd_flag = True
        Plot_interface.lc5.display_legend=True
        dfPyCCD = Plot_interface.sample_df

        dfPyCCD['pixel_qa'][dfPyCCD['pixel_qa'] > 4] = 0

        #TODO: Paramaterize everything
        params = {'QA_BITPACKED': False,
                  'QA_FILL': 255,
                  'QA_CLEAR': 0,
                  'QA_WATER': 1,
                  'QA_SHADOW': 2,
                  'QA_SNOW': 3,
                  'QA_CLOUD': 4}

        dates = np.array(dfPyCCD['ord_time'])
        blues = np.array(dfPyCCD['BLUE'])
        greens = np.array(dfPyCCD['GREEN'])
        reds = np.array(dfPyCCD['RED'])
        nirs = np.array(dfPyCCD['NIR'])
        swir1s = np.array(dfPyCCD['SWIR1'])
        swir2s = np.array(dfPyCCD['SWIR2'])
        thermals = np.array(dfPyCCD['THERMAL'])
        qas = np.array(dfPyCCD['pixel_qa'])
        results = ccd.detect(dates, blues, greens, reds, nirs, swir1s, swir2s, thermals, qas, params=params)

        band_names = ['Blue SR', 'Green SR', 'Red SR', 'NIR SR', 'SWIR1 SR', 'SWIR2 SR','THERMAL']
        plotlabel = band_names[Plot_interface.band_index1]

        plot_arrays = [blues, greens, reds, nirs, swir1s, swir2s]
        plotband = plot_arrays[Plot_interface.band_index1]
        Plot_interface.plot_pyccd(results, Plot_interface.band_index1,
                                  plotband, dates, (0, 4000), 'PyCCD Results', 'sample_ts')

    def run_pyccd2(b):
        # Run pyCCD on current point
        Plot_interface.pyccd_flag2 = True

        # Display the legend
        Plot_interface.lc7.display_legend=True

        dfPyCCD = Plot_interface.click_df

        # First two lines no longer required bc we are removing NA's when we load the TS
        dfPyCCD['pixel_qa'][dfPyCCD['pixel_qa'] > 4] = 0

        #TODO: Paramaterize everything
        params = {'QA_BITPACKED': False,
                  'QA_FILL': 255,
                  'QA_CLEAR': 0,
                  'QA_WATER': 1,
                  'QA_SHADOW': 2,
                  'QA_SNOW': 3,
                  'QA_CLOUD': 4}

        dates = np.array(dfPyCCD['ord_time'])
        blues = np.array(dfPyCCD['BLUE'])
        greens = np.array(dfPyCCD['GREEN'])
        reds = np.array(dfPyCCD['RED'])
        nirs = np.array(dfPyCCD['NIR'])
        swir1s = np.array(dfPyCCD['SWIR1'])
        swir2s = np.array(dfPyCCD['SWIR2'])
        thermals = np.array(dfPyCCD['THERMAL'])
        qas = np.array(dfPyCCD['pixel_qa'])
        results = ccd.detect(dates, blues, greens, reds, nirs, swir1s, swir2s, thermals, qas, params=params)

        band_names = ['Blue SR', 'Green SR', 'Red SR', 'NIR SR', 'SWIR1 SR', 'SWIR2 SR','THERMAL']
        plotlabel = band_names[Plot_interface.band_index2]

        plot_arrays = [blues, greens, reds, nirs, swir1s, swir2s]
        plotband = plot_arrays[Plot_interface.band_index2]
        Plot_interface.plot_pyccd(results, Plot_interface.band_index2,
                                  plotband, dates, (0, 4000), 'PyCCD Results', 'clicked_ts')

    ylim.observe(change_yaxis)
    xlim.observe(change_xaxis)
    ylim2.observe(change_yaxis2)
    xlim2.observe(change_xaxis2)
    next_pt.on_click(advance)
    previous_pt.on_click(decrease)
    pyccd_button.on_click(run_pyccd)
    pyccd_button2.on_click(run_pyccd2)
    clear_layers.on_click(clear_map)
    band_selector1.observe(on_band_selection1, names='value')
    band_selector2.observe(on_band_selection2, names='value')

    image_band_1.observe(change_image_band1, names='value')
    image_band_2.observe(change_image_band2, names='value')
    image_band_3.observe(change_image_band3, names='value')

    lc2.on_element_click(click_event)
    lc2.tooltip=hover_label
    lc2.on_hover(hover_event)

    lc3.on_element_click(click_event2)
    lc3.tooltip=hover_label
    lc3.on_hover(hover_event)

    idBox.on_submit(go_to_sample)


    dc.on_draw(handle_draw)
    m.add_control(dc)
    m.add_control(ipyleaflet.LayersControl())
