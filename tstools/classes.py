# Classes for individual projects
import tstools.utils as utils
import tstools.sql as sql
import tstools.sheets as sheets
import tstools.leaflet_tools as lft
import tstools.ccd as ccd_tools
import ipyleaflet
import os, qgrid, datetime, sqlite3
import pandas as pd
import tstools.plots as plots
import ipywidgets as widgets

# Sample interpretation to collect training data for MEaSUREs
class measures(object):

    def __init__(self):
        measures.sheet = None
        measures.sheet2 = None
        measures.band_index1 = 4
        measures.band_index2 = 4
        measures.pyccd_flag = False
        measures.pyccd_flag2 = False
        measures.table = None
        conn = sqlite3.connect(measures.dbPath)
        measures.current_id = measures.current_id
        measures.c = conn.cursor()
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

    # Set up database
    dbPath = os.getcwd() + '/measures_database'
    command = '''CREATE TABLE measures
                  (id text, lat text, lon text, year1 text, year2 text, direction text, coverType text,
                  condition text, change text, chaOther text, confCA text,
                  class text, water text, bare text, albedo text, use text,
                  height text, transport text, impervious text, density text,
                  vegType1 text, herbaceous text, shrub text, forestPhenology text,
                  leafType text, location text, confidence real, notes text,
                  byear text, brange1 text, brange2 text)'''
    conn = sql.make_db(dbPath, command)

    # Widgets

    # Sliders
    years = plots.make_range_slider([1990, 1990], 1990, 2018, 1, 'Years:')
    break_years = plots.make_range_slider([1990, 1990], 1990, 2018, 1, 'Years:')
    break_year = plots.make_slider(1990, 1990, 2018, 1, 'Years:')
    confidence = plots.make_slider(0, 0, 3, 1, 'Confidence:')
    ca_confidence = plots.make_slider(0, 0, 3, 1, '')

    ylim = plots.make_range_slider([0, 4000], -10000, 10000, 500, 'YLim:')
    xlim = plots.make_range_slider([2000, 2018], 1984, 2019, 1, 'XLim:')

    ylim2 = plots.make_range_slider([0, 4000], -10000, 10000, 500, 'YLim:')
    xlim2 = plots.make_range_slider([2000, 2018], 1984, 2019, 1, 'XLim:')

    # Dropdown boxes
    drop1 = plots.make_drop('Persistant Ice?', ['Persistant Ice?', 'Yes','No'],  'Decision 2')
    drop2 = plots.make_drop('Decision 3', ['Decision 3'], 'Decision 3')
    drop3 = plots.make_drop('Decision 4', ['Decision 4'], 'Decision 4')
    drop4 = plots.make_drop('Decision 5', ['Decision 5'], 'Decision 5')
    drop5 = plots.make_drop('Decision 6', ['Decision 6'], 'Decision 6')
    drop6 = plots.make_drop('Decision 7', ['Decision 7'], 'Decision 7')
    drop7 = plots.make_drop('Decision 8', ['Decision 8'], 'Decision 8')
    drop8 = plots.make_drop('Decision 9', ['Decision 9'], 'Decision 9')
    drop9 = plots.make_drop('Stable', ['Stable','Transitional','Break'], 'Label Type:')
    drop0 = plots.make_drop('Dominant or Secondary?', ['Dominant or Secondary?','Dominant','Secondary'],
                            'Decision 1')

    band_selector1 = plots.make_drop('SWIR1',band_list,'Select band')
    band_selector2 = plots.make_drop('SWIR1',band_list,'Select band')
    image_band_1 = plots.make_drop('RED',band_list,'Red:')
    image_band_2 = plots.make_drop('GREEN',band_list,'Green:')
    image_band_3 = plots.make_drop('BLUE',band_list,'Blue:')

    # Checkbox
    color_check = plots.make_checkbox(False, 'Color DOY', False)

    # Select multiple
    veg_selector = plots.make_selector(['Veg Type'],['Veg Type', 'Cropland','Plantation','Wetland',
                                       'Riparian/Flood','Mangrove'],'Veg Type:',disabled=True)
    change_selector = plots.make_selector(['None'],['None','Deforestation/Logging', 'Fire', 'Insect damage',
                                          'Urban Dev.', 'Flooding','Decline/Degradation','Regrowth',
                                          'Riparian/Water shift','Other (Specify)'], 'Change Agent:')
    direction = plots.make_selector(['None'],['None','Veg Increase','Veg Decrease','Water Increase',
                                    'Water Decrease','Bare Increase','Bare Decrease','Urban Increase',
                                    'Urban Decrease','Albedo Increase','Albedo Decrease'],'Directional Change:')

    # Text boxes
    change_other = plots.make_text('Specify other','Specify other','Other:')
    notes = plots.make_text_large('Enter any useful or interesting information about the sample',
                                  'Enter any useful or interesting information about the sample',
                                  'Notes',layout=widgets.Layout(width='70%'))
    spreadsheet = plots.make_text('Google Spreadsheet Credential JSON',
                                  'Google Spreadsheet Credential JSON', 'Credentials:')
    spreadName = plots.make_text('Google Spreadsheet Name',
                                  'Google Spreadsheet Name', 'SS Name:')
    sampleWidget = plots.make_text('Path to sample feature collection',
                                   'Path to sample feature collection','Path:')

    stretch_min = plots.make_text_float(0, 0, 'Min:')
    stretch_max = plots.make_text_float(1450, 0, 'Max:')
    idBox = plots.make_text('0','0','ID:')

    # Buttons
    validate = plots.make_button(False, 'Validate',icon='check')
    save_button = plots.make_button(False, 'Save',icon='')
    load_button = plots.make_button(False, 'Load',icon='')

    next_pt = plots.make_button(False, 'Next point', icon='')
    previous_pt = plots.make_button(False, 'Previous point', icon='')
    pyccd_button = plots.make_button(False, 'Run PyCCD 1', icon='')
    pyccd_button2 = plots.make_button(False, 'Run PyCCD 2', icon='')
    clear_layers = plots.make_button(False, 'Clear Map', icon='')

    # Validate
    valid = plots.make_valid(False, 'Not Saved', '')
    valid_load = plots.make_valid(False, 'Not Loaded','')

    # HTML
    pt_message = plots.make_html('Current ID: ')
    time_label = plots.make_html('')
    selected_label = plots.make_html('ID of selected point')
    hover_label = plots.make_html('Test Value')
    text_brush = plots.make_html('Selected year range:')
    kml_link = plots.make_html('KML:')
    error_label = plots.make_html('Load a point')

    # Table
    table_widget = qgrid.show_grid(table, show_toolbar=False)



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



    # Axis
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

    def reset_drops():
        measures.drop4.set_trait('options', ['Decision 4'])
        measures.drop5.set_trait('options', ['Decision 5'])
        measures.drop6.set_trait('options', ['Decision 6'])
        measures.drop7.set_trait('options', ['Decision 7'])
        measures.drop8.set_trait('options', ['Decision 8'])
        measures.veg_selector.disabled = True

    def drop1_clicked(selection):
        """ Generate secondary class selector after initial class is chosen """
        if selection.new == 'No':
            measures.drop2.set_trait('options', ['>30% Vegetated?','Yes', 'No'])
        elif selection.new == 'Yes':
            measures.drop2.set_trait('options', ['Ice/Snow'])
            measures.drop3.set_trait('options', ['No other information needed'])
            measures.reset_drops()

    def drop2_clicked(selection):
        """ Generate vegetation class information after initial class is chosen """
        if '>30% Vegetated?' in measures.drop2.options:
            if selection.new == 'Yes':
                measures.drop3.set_trait('options', ['Density','Closed (60-70%)',
                                                     'Open (30-60%)', 'Sparse (<30%)'])
                measures.veg_selector.disabled = False
                measures.drop4.set_trait('options', ['Trees?','Yes', 'No'])
            elif selection.new == 'No':
                measures.drop3.set_trait('options', ['Dominant Cover?', 'Water',
                                                     'Bare','Developed'])
                measures.drop4.set_trait('options', ['Decision 4'])
                measures.drop5.set_trait('options', ['Decision 5'])
                measures.drop6.set_trait('options', ['Decision 6'])
                measures.drop7.set_trait('options', ['Decision 7'])
                measures.drop8.set_trait('options', ['Decision 8'])
                measures.veg_selector.disabled = True

        else:
            measures.drop3.set_trait('options', ['No Other Information Needed'])

    def drop3_clicked(selection):
        """ Generate third class selector after initial class is chosen """
        if 'Dominant Cover?' in measures.drop3.options:
            measures.veg_selector.disabled = True
            if selection.new == 'Water':
                measures.drop4.set_trait('options', ['Water Type','Shore/Inter tidal',
                                                     'Shallows', 'River','Lake/Reservoir','Ocean'])
            elif selection.new == 'Bare':
                measures.drop4.set_trait('options', ['Bare Type', 'Soil','Rock','Quarry (Active)',
                                                     'Beach/Sand'])
            elif selection.new == 'Developed':
                measures.drop4.set_trait('options', ['Surface Albedo', 'High','Low','Mixed'])
                measures.drop5.set_trait('options', ['Use','Residential', 'Commercial/Industrial'])
                measures.drop6.set_trait('options', ['Building Height','No Buildings','1-2 Stories',
                                                     '3-5 Stories','5+ Stories'])
                measures.drop7.set_trait('options', ['Transport','Road','Not Applicable'])
                measures.drop8.set_trait('options', ['% Impervious','High (60-100)','Medium (30-60)',
                                                     'Low (<30)'])

    def drop4_clicked(selection):
        """ Generate fourth class selector after initial class is chosen """
        if 'Trees?' in measures.drop4.options:
            if selection.new == 'Yes':
                measures.drop5.set_trait('options', ['Height >5m & Canopy >30%','Yes', 'No'])
            elif selection.new == 'No':
                measures.drop5.set_trait('options', ['Herbaceous Type','Grassland', 'Pasture','Lawn/Urban Grass','Moss/Lichen'])


    def drop5_clicked(selection):
        """ Generate fifth class selector after initial class is chosen """
        if 'Height >5m & Canopy >30%' in measures.drop5.options:
            if selection.new == 'Yes':
                measures.drop6.set_trait('options', ['Forest Type','Evergreen', 'Deciduous','Mixed'])
                measures.drop7.set_trait('options', ['Leaf Type','Broad', 'Needle','Unsure'])
                measures.drop8.set_trait('options', ['Location','Interior', 'Edge'])

            elif selection.new == 'No':
                measures.drop6.set_trait('options', ['Shrub Type','Evergreen', 'Deciduous','Mixed'])

    def check_val_status(selection):
        """ Check the validity of the current sample and change valid widget accordingly """
        selected_secondary_lc = False
        wrote_correct_lc = False
        if measures.second_class_drop.value != 'Secondary Class Information':
            selected_secondary_lc = True
        else:
            print("Must specify secondary class information!")
        if measures.lc.value.capitalize() == measures.textClass.value.capitalize():
            wrote_correct_lc = True
        if selected_secondary_lc and wrote_correct_lc:
            measures.valid.value = True
            measures.save_button.disabled = False

    def load_everything(sender):
        # def load_sheet(spreadsheet, worksheet, cred_file):
        measures.sheet = sheets.load_sheet(measures.spreadName.value, 0,  measures.spreadsheet.value)
        measures.sheet1 = sheets.load_sheet(measures.spreadName.value, 0,  measures.spreadsheet.value)

        # Load the sample as a feature collection
        sample_path = measures.sampleWidget.value
        fc_df = utils.fc2dfgeo(sample_path)
        measures.fc_df, first_index = utils.check_id(fc_df)
        measures.valid_load.value = True
        measures.valid_load.description = 'Loaded!'
        measures.current_id = first_index - 1

    def turn_on_break_years(selection):
        if selection.new == 'Break':
            measures.break_years.disabled = False
            measures.break_year.disabled = False
        else:
            measures.break_years.disabled = True
            measures.break_year.disabled = True

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
        measures.change_table(0)
        measures.valid.value = False
        measures.description='Not Saved'

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
        measures.change_table(0)
        measures.valid.value = False
        measures.description='Not Saved'

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
        measures.valid.value = False
        measures.description='Not Saved'
        measures.map_point()
        measures.get_ts()
        measures.plot_ts()

    def change_table(b):
        # Update the table based on current ID

        # Get header
        cursor = measures.c.execute('select * from measures')
        names = list(map(lambda x: x[0], cursor.description))
        previous_inputs = pd.DataFrame()
        for i, row in enumerate(measures.c.execute("SELECT * FROM measures WHERE id = '%s'" % measures.current_id)):
            previous_inputs[i] = row
        previous_inputs = previous_inputs.T
        if previous_inputs.shape[0] > 0:
            previous_inputs.columns = names
        measures.table_widget.df = previous_inputs

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
        #plots.add_plot_ts(df, measures.lc4, band, color_marks)
        #plots.add_plot_ts(df, measures.lc5, band, color_marks)

        plots.add_plot_doy(df, measures.lc8, band, color_marks)

        #if measures.pyccd_flag:
        #    measures.do_pyccd(0)

    def do_pyccd(b):
        pyccd_flag = measures.pyccd_flag
        display_legend = measures.lc5.display_legend
        dfPyCCD = measures.sample_df
        band_index = measures.band_index1
        ccd_tools.run_pyccd(pyccd_flag, display_legend, dfPyCCD, band_index)

    def do_pyccd2(b):
        pyccd_flag = measures.pyccd_flag2
        display_legend = measures.lc7.display_legend
        dfPyCCD = measures.click_df
        band_index = measures.band_index1
        ccd_tools.run_pyccd(pyccd_flag, display_legend, dfPyCCD, band_index)



    # Widget interactions
    validate.on_click(check_val_status)
    # Primary class selector action
    drop1.observe(drop1_clicked, 'value')
    # Secondary class selector action
    drop2.observe(drop2_clicked, 'value')
    # Third class selector action
    drop3.observe(drop3_clicked, 'value')
    drop4.observe(drop4_clicked, 'value')
    drop5.observe(drop5_clicked, 'value')
    drop9.observe(turn_on_break_years, 'value')

    # Load database and sample
    load_button.on_click(load_everything)

    # Map
    dc = ipyleaflet.DrawControl(marker={'shapeOptions': {'color': '#ff0000'}},
                                 polygon={}, circle={}, circlemarker={}, polyline={})

    zoom = 5
    #layout = {'height': '100px'}
    #layout = {'flex': '1'}
    #layout = widgets.Layout(flex='1')
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
