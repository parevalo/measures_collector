# Classes for individual projects

import tstools.utils as utils
import tstools.sql as sql
import tstools.sheets as sheets
import tstools.leaflet_tools as lft
import tstools.ccd as ccd_tools
import ipyleaflet
import os, qgrid, datetime, sqlite3, time
import pandas as pd
import tstools.plots as plots
import ipywidgets as widgets




class pyccd_explorer(object):

    def __init__(self):
        measures.band_index1 = 4
        measures.band_index2 = 4
        measures.pyccd_flag = False
        measures.pyccd_flag2 = False
        measures.minv = 0
        measures.maxv = 6000
        measures.b1 = 'SWIR1'
        measures.b2 = 'NIR'
        measures.b3 = 'RED'

    # Starting variables
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
    current_id = 0

    ylim = plots.make_range_slider([0, 4000], -10000, 10000, 500, 'YLim:')
    xlim = plots.make_range_slider([2000, 2018], 1984, 2019, 1, 'XLim:')

    ylim2 = plots.make_range_slider([0, 4000], -10000, 10000, 500, 'YLim:')
    xlim2 = plots.make_range_slider([2000, 2018], 1984, 2019, 1, 'XLim:')

    band_selector1 = plots.make_drop('SWIR1',band_list,'Select band')
    band_selector2 = plots.make_drop('SWIR1',band_list,'Select band')
    image_band_1 = plots.make_drop('RED',band_list,'Red:')
    image_band_2 = plots.make_drop('GREEN',band_list,'Green:')
    image_band_3 = plots.make_drop('BLUE',band_list,'Blue:')

    # Checkbox
    color_check = plots.make_checkbox(False, 'Color DOY', False)

    stretch_min = plots.make_text_float(0, 0, 'Min:')
    stretch_max = plots.make_text_float(1450, 0, 'Max:')
    idBox = plots.make_text('0','0','ID:')

    load_button = plots.make_button(False, 'Load',icon='')

    next_pt = plots.make_button(False, 'Next point', icon='')
    previous_pt = plots.make_button(False, 'Previous point', icon='')
    pyccd_button = plots.make_button(False, 'Run PyCCD 1', icon='')
    pyccd_button2 = plots.make_button(False, 'Run PyCCD 2', icon='')
    clear_layers = plots.make_button(False, 'Clear Map', icon='')

    # HTML
    pt_message = plots.make_html('Current ID: ')
    coord_message = plots.make_html('Lat, Lon: ')
    time_label = plots.make_html('')
    selected_label = plots.make_html('ID of selected point')
    hover_label = plots.make_html('Test Value')
    text_brush = plots.make_html('Selected year range:')
    kml_link = plots.make_html('KML:')
    error_label = plots.make_html('Load a point')


    # Plots

    # Scales
    # Dates
    lc1_x = plots.make_bq_scale('date',datetime.date(xlim.value[0], 2, 1), datetime.date(xlim.value[1], 1, 1))
    lc1_x2 = plots.make_bq_scale('date',datetime.date(xlim.value[0], 2, 1), datetime.date(xlim.value[1], 1, 1))

    # DOY
    lc1_x3 = plots.make_bq_scale('linear',0, 365)

    # Reflectance
    lc2_y = plots.make_bq_scale('linear', ylim.value[0], ylim.value[1])
    lc2_y2 = plots.make_bq_scale('linear', ylim.value[0], ylim.value[1])

    # plots
    lc2 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x, 'y': lc2_y},[1,1],
                            {'click': 'select', 'hover': 'tooltip'},
                            {'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
                            {'opacity': 0.5}, display_legend=True, labels=['Sample point'])

    lc3 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x2, 'y': lc2_y2},[1,1],
                            {'click': 'select', 'hover': 'tooltip'},
                            {'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
                            {'opacity': 0.5}, display_legend=True, labels=['Clicked point'])

    lc4 = plots.make_bq_plot('lines', [], [], {'x': lc1_x, 'y': lc2_y}, [1,1],
                             {}, {}, {}, colors=['black'], stroke_width=3)

    lc5 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x, 'y': lc2_y}, [1,1], {}, {},
                             {}, labels = ['Model Endpoint'], colors=['red'], marker='triangle-up')

    lc6 = plots.make_bq_plot('lines', [], [], {'x': lc1_x2, 'y': lc2_y2}, [1,1],
                             {}, {}, {}, colors=['black'], stroke_width=3)

    lc7 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x2, 'y': lc2_y2}, [1,1], {}, {},
                             {}, labels = ['Model Endpoint'], colors=['red'], marker='triangle-up')

    lc8 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x3, 'y': lc2_y},[1,1],
                            {'click': 'select', 'hover': 'tooltip'},
                            {'opacity': 1.0, 'fill': 'DarkOrange', 'stroke': 'Red'},
                            {'opacity': 0.5}, display_legend=True, labels=['Sample point'])


    x_ax1 = plots.make_bq_axis('Date',lc1_x,num_ticks=6,tick_format='%Y', orientation='horizontal')
    x_ax2 = plots.make_bq_axis('Date',lc1_x2,num_ticks=6,tick_format='%Y', orientation='horizontal')
    x_ax3 = plots.make_bq_axis('DOY',lc1_x3,num_ticks=6, orientation='horizontal')

    y_ay1 = plots.make_bq_axis('SWIR1', lc2_y, orientation='vertical')
    y_ay2 = plots.make_bq_axis('SWIR1', lc2_y2, orientation='vertical')


    # Figures
    fig = plots.make_bq_figure([lc2, lc4, lc5], [x_ax1, y_ay1], {'height': '300px', 'width': '100%'},
                               'Sample TS')
    fig2 = plots.make_bq_figure([lc3, lc6, lc7], [x_ax2, y_ay2], {'height': '300px', 'width': '100%'},
                               'Clicked TS')
    fig3 = plots.make_bq_figure([lc8], [x_ax3, y_ay1], {'height': '300px', 'width': '100%'},
                               'Clicked TS')


    # Functions


    def load_everything(sender):
        # Load the sample as a feature collection
        sample_path = measures.sampleWidget.value
        fc_df = utils.fc2dfgeo(sample_path)
        measures.fc_df, first_index = utils.check_id(fc_df)
        measures.current_id = first_index - 1
        measures.reset_everything()

    def change_yaxis(value):
        measures.lc2_y.min = measures.ylim.value[0]
        measures.lc2_y.max = measures.ylim.value[1]

    def change_xaxis(value):
        measures.lc1_x.min = datetime.date(measures.xlim.value[0], 2, 1)
        measures.lc1_x.max = datetime.date(measures.xlim.value[1], 2, 1)
        measures.year_range = [measures.xlim.value[0], measures.xlim.value[1]]

    def change_yaxis2(value):
        measures.lc2_y2.min = measures.ylim2.value[0]
        measures.lc2_y2.max = measures.ylim2.value[1]

    def change_xaxis2(value):
        measures.lc1_x2.min = datetime.date(measures.xlim2.value[0], 2, 1)
        measures.lc1_x2.max = datetime.date(measures.xlim2.value[1], 2, 1)

    def hover_event(self, target):
        measures.hover_label.value = str(target['data']['x'])

    def advance(b):
        # Plot point in map
        measures.lc4.x = []
        measures.lc4.y = []
        measures.lc5.x = []
        measures.lc5.y = []
        measures.lc5.display_legend=False
        measures.pyccd_flag = False
        measures.current_id += 1
        measures.pt_message.value = "Point ID: {}".format(measures.current_id)
        measures.map_point()
        measures.get_ts()
        measures.plot_ts()

    def decrease(b):
        # Plot point in map
        measures.lc4.x = []
        measures.lc4.y = []
        measures.lc5.x = []
        measures.lc5.y = []
        measures.lc5.display_legend=False
        measures.pyccd_flag = False
        measures.current_id -= 1
        measures.pt_message.value = "Point ID: {}".format(measures.current_id)
        measures.map_point()
        measures.get_ts()
        measures.plot_ts()

    # Go to a specific sample
    def go_to_sample(b):
        # Plot point in map
        measures.lc4.x = []
        measures.lc4.y = []
        measures.lc5.x = []
        measures.lc5.y = []
        measures.lc5.display_legend=False
        measures.pyccd_flag = False
        measures.current_id = int(b.value)
        measures.pt_message.value = "Point ID: {}".format(measures.current_id)
        measures.map_point()
        measures.get_ts()
        measures.plot_ts()

    # Functions for changing image stretch
    def change_image_band1(change):
        new_band = change['new']
        measures.b1 = new_band
    def change_image_band2(change):
        new_band = change['new']
        measures.b2 = new_band
    def change_image_band3(change):
        new_band = change['new']
        measures.b3 = new_band

    # Band selection for sample point
    def on_band_selection1(change):
        band_index = change['owner'].index
        measures.band_index1 = band_index
        measures.plot_ts()

    # Band selection for clicked point
    def on_band_selection2(change):
        new_band = change['new']
        band_index = change['owner'].index
        measures.band_index2 = band_index
        measures.lc3.x = measures.click_df['datetime']
        measures.lc3.y = measures.click_df[new_band]
        measures.x_ay2.label = new_band
        if measures.pyccd_flag2:
            measures.do_pyccd2(0)

    def clear_map(b):
        lft.clear_map(measures.m, streets=True)
        measures.map_point()

    def add_image(self, target):
        m = measures.m
        df = measures.sample_df
        current_band = measures.band_list[measures.band_index1]
        sample_col = measures.sample_col
        stretch_min = measures.stretch_min
        stretch_max = measures.stretch_max
        b1 = measures.b1
        b2 = measures.b2
        b3 = measures.b3
        lft.click_event(target,m, current_band, df, sample_col, stretch_min, stretch_max,
                        b1, b2, b3)

    def add_image2(self, target):
        m = measures.m
        df = measures.click_df
        current_band = measures.band_list[measures.band_index2]
        sample_col = measures.click_col
        stretch_min = measures.minv
        stretch_max = measures.maxv
        b1 = measures.b1
        b2 = measures.b2
        b3 = measures.b3
        lft.click_event(target,m, current_band, df, sample_col, stretch_min, stretch_max,
                        b1, b2, b3)

    def do_draw(self, action, geo_json):
        current_band = measures.band_list[measures.band_index2]
        year_range = measures.year_range
        doy_range = measures.doy_range
        _col, _df = utils.handle_draw(action, geo_json, current_band, year_range, doy_range)
        measures.click_df = _df
        measures.click_col = _col
        measures.lc6.x = []
        measures.lc6.y = []
        measures.lc7.x = []
        measures.lc7.y = []

        measures.lc3.x = measures.click_df['datetime']
        measures.lc3.y = measures.click_df[current_band]

        if measures.color_check.value == False:
            measures.lc3.colors = list(measures.point_color)
        else:
            measures.lc3.colors = list(measures.click_df['color'].values)

    def map_point():
        zoom = 12
        kml = measures.kml_link
        name = 'Sample point'
        data = measures.fc_df['geometry'][measures.current_id]
        measures.coord_message.value = "Lat, Lon: {}".format(data['coordinates'])
        lft.add_map_point(data, zoom, measures.m, kml, name)

    def get_ts():

        measures.error_label.value = 'Loading'
        coords = measures.fc_df['geometry'][measures.current_id]['coordinates']
        year_range = measures.year_range
        doy_range = measures.doy_range

        measures.current_band = measures.band_list[measures.band_index1]
        measures.sample_col = utils.get_full_collection(coords, year_range, doy_range)
        measures.sample_df = utils.get_df_full(measures.sample_col, coords).dropna()
        measures.error_label.value = 'Point Loaded!'

    def plot_ts():
        df = measures.sample_df

        if measures.color_check.value == True:
            color_marks = list(measures.sample_df['color'].values)
        else:
            color_marks = list(measures.point_color)

        band = measures.band_list[measures.band_index1]

        plots.add_plot_ts(df, measures.lc2, band, color_marks)

        plots.add_plot_doy(df, measures.lc8, band, color_marks)

        if measures.pyccd_flag:
            measures.do_pyccd(0)

    def do_pyccd(b):
        pyccd_flag = measures.pyccd_flag
        display_legend = measures.lc5.display_legend
        dfPyCCD = measures.sample_df
        band_index = measures.band_index1
        results = ccd_tools.run_pyccd(pyccd_flag, display_legend, dfPyCCD, band_index)

        ccd_tools.plot_pyccd(dfPyCCD, results, band_index,(0, 4000), measures.lc4, measures.lc5)

    def do_pyccd2(b):
        pyccd_flag = measures.pyccd_flag2
        display_legend = measures.lc7.display_legend
        dfPyCCD = measures.click_df
        band_index = measures.band_index1
        results = ccd_tools.run_pyccd(pyccd_flag, display_legend, dfPyCCD, band_index)

        ccd_tools.plot_pyccd(dfPyCCD, results, band_index,(0, 4000), measures.lc6, measures.lc7)


    # Load database and sample
    load_button.on_click(load_everything)

    # Map
    dc = ipyleaflet.DrawControl(marker={'shapeOptions': {'color': '#ff0000'}},
                                 polygon={}, circle={}, circlemarker={}, polyline={})

    zoom = 5
    layout = widgets.Layout(width='50%')
    center = (3.3890701010382958, -67.32297252983098)
    m = lft.make_map(zoom, layout, center)
    m = lft.add_basemap(m, ipyleaflet.basemaps.Esri.WorldImagery)

    # Display controls
    ylim.observe(change_yaxis)
    xlim.observe(change_xaxis)
    ylim2.observe(change_yaxis2)
    xlim2.observe(change_xaxis2)
    clear_layers.on_click(clear_map)
    band_selector1.observe(on_band_selection1, names='value')
    band_selector2.observe(on_band_selection2, names='value')
    image_band_1.observe(change_image_band1, names='value')
    image_band_2.observe(change_image_band2, names='value')
    image_band_3.observe(change_image_band3, names='value')

    # .samples
    next_pt.on_click(advance)
    previous_pt.on_click(decrease)

    # PyCCD
    pyccd_button.on_click(do_pyccd)
    pyccd_button2.on_click(do_pyccd2)


    # Plots
    lc2.on_element_click(add_image)
    lc2.tooltip=hover_label
    lc2.on_hover(hover_event)

    lc3.on_element_click(add_image2)
    lc3.tooltip=hover_label
    lc3.on_hover(hover_event)

    idBox.on_submit(go_to_sample)

    # Mapping
    dc.on_draw(do_draw)
    m.add_control(dc)
    m.add_control(ipyleaflet.LayersControl())

