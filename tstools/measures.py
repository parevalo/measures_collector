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


    ####### Starting Variables #######

    pyccd_flag = False
    pyccd_flag2 = False
    current_band = ''
    band_index1 = 4
    band_index2 = 4
    click_col = ''
    point_color = ['#43a2ca']
    click_df = pd.DataFrame()
    click_geojson = ''
    box_geojson = ''
    click_trainbox = ''
    sample_col = ''
    sample_df = pd.DataFrame()
    samplept_geojson = ''
    PyCCDdf = pd.DataFrame()
    table = pd.DataFrame()
    band_list =['BLUE', 'GREEN', 'RED','NIR','SWIR1','SWIR2', 'BRIGHTNESS','GREENNESS','WETNESS']
    year_range = [ 1986, 2018 ]
    doy_range = [ 1, 365 ]
    step = 1 #in years
    current_id = 0


    ####### Database #######

    dbPath = os.getcwd() + '/measures_database'

    # Old, out of order, and missing 2 columns:
#    command = '''CREATE TABLE measures
#                  (id text, lat text, lon text, year1 text, year2 text, direction text, coverType text,
#                  condition text, change text, chaOther text, confCA text,
#                  class text, water text, bare text, albedo text, use text,
#                  height text, transport text, impervious text, density text,
#                  vegType1 text, herbaceous text, shrub text, forestPhenology text,
#                  leafType text, location text, confidence real, notes text,
#                  byear text, brange1 text, brange2 text)'''

    command = '''CREATE TABLE measures
                  (id text, lat text, lon text, year1 text, year2 text, coverType text,
                  condition text, class1 text, water text, bare text, albedo text, use text,
                  height text, transport text, impervious text, density text, vegType text, herbType text,
                  shrubType text, phenology text, leafType text, location text, conf text, notes1 text,
                  segType text, direction text, changeAgent text, confCA text, ca_other text, seg_notes text,
                  breakYear text, breakRange1 text, breakRange2 text)'''
    conn = sql.make_db(dbPath, command)


    ###### Widgets ######

    # Sliders
    years = plots.make_range_slider([1990, 1991], 1990, 2018, 1, 'Years:')
    break_years = plots.make_range_slider([1990, 1991], 1990, 2018, 1, 'Confidence:', disabled=True)
    break_year = plots.make_slider(1990, 1991, 2018, 1, 'Year:', disabled=True)
    confidence = plots.make_slider(0, 0, 3, 1, 'Confidence:')
    ca_confidence = plots.make_slider(0, 0, 3, 1, '', disabled=True)
    b_ca_confidence = plots.make_slider(0, 0, 3, 1, '', disabled=True)

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
    drop9 = plots.make_drop('Select type', ['Select type', 'Stable','Transitional'], '')
    drop0 = plots.make_drop('Dominant or Secondary?', ['Dominant or Secondary?','Dominant','Secondary'],
                            'Decision 1')

    band_selector1 = plots.make_drop('SWIR1',band_list,'Select band')
    band_selector2 = plots.make_drop('SWIR1',band_list,'Select band')
    image_band_1 = plots.make_drop('SWIR1',band_list,'Red:')
    image_band_2 = plots.make_drop('NIR',band_list,'Green:')
    image_band_3 = plots.make_drop('RED',band_list,'Blue:')

    # Checkbox
    color_check = plots.make_checkbox(False, 'Color DOY', False)
    break_check = plots.make_checkbox(False, 'Land Cover Change in TS?', False)
    click_train = plots.make_checkbox(False, 'Collect TS training', False)

    # Select multiple
    veg_selector = plots.make_selector(['Select a modifier'],['Select a modifier', 'None', 'Cropland','Plantation','Wetland',
                                       'Riparian/Flood','Mangrove'],'Veg Type:',disabled=True)
    change_selector = plots.make_selector(['None'],['None','Deforestation/Logging', 'Fire', 'Insect damage',
                                          'Urban Dev.', 'Flooding','Decline/Degradation','Regrowth',
                                          'Riparian/Water shift', 'Unknown', 'Other (Specify)'], '', disabled=True)
    b_change_selector = plots.make_selector(['None'],['None','Deforestation/Logging', 'Fire', 'Insect damage',
                                          'Urban Dev.', 'Flooding','Decline/Degradation','Regrowth',
                                          'Riparian/Water shift','Other (Specify)'], '',disabled=True)
    direction = plots.make_selector(['NA'],['NA','Unknown','Veg Increase','Veg Decrease','Water Increase',
                                    'Water Decrease','Bare Increase','Bare Decrease','Urban Increase',
                                    'Urban Decrease','Albedo Increase','Albedo Decrease'],'', disabled=True)
    b_direction = plots.make_selector(['NA'],['NA','Unknown','Veg Increase','Veg Decrease','Water Increase',
                                    'Water Decrease','Bare Increase','Bare Decrease','Urban Increase',
                                    'Urban Decrease','Albedo Increase','Albedo Decrease'],'', disabled=True)

    # Text boxes
    change_other = plots.make_text('Specify other','Specify other','Other:', disabled=True)
    b_change_other = plots.make_text('Specify other','Specify other','Other:', disabled=True)
    notes = plots.make_text_large('Enter any useful or interesting information about the land cover of this sample',
                                  '',
                                  'Notes', layout=widgets.Layout()) #,layout=widgets.Layout(width='70%'))
    notes_seg_trend = plots.make_text_large('Enter any useful or interesting information about the Time Trend of this sample',
                                            '',
                                            'Notes', layout=widgets.Layout())
    notes_break = plots.make_text_large('Enter any useful or interesting information about the Break in the time series',
                                            '',
                                            'Notes', layout=widgets.Layout(), disabled=True) # TODO: save this
    spreadsheet = plots.make_text('Google Spreadsheet Credential JSON',
                                  'Google Spreadsheet Credential JSON', 'Credentials:')
    spreadName = plots.make_text('Google Spreadsheet Name',
                                  'Google Spreadsheet Name', 'SS Name:')
    sampleWidget = plots.make_text('Path to sample feature collection',
                                   'Path to sample feature collection','Path:')

    stretch_min = plots.make_text_float(0, 0, 'Min:')
    stretch_max = plots.make_text_float(6000, 6000, 'Max:')
    zoom_box = plots.make_text_float(12, 12, 'Zoom:')
    idBox = plots.make_text('0','0','ID:')

    # Buttons
    validate = plots.make_button(False, 'Validate',icon='check')
    save_button = plots.make_button(False, 'Save Segment LC',icon='')
    b_save_button = plots.make_button(False, 'Save Break',icon='', disabled=True) #TODO: does nothing
    load_button = plots.make_button(False, 'Load',icon='')
    toggle_pyccd_button = plots.make_button(False, 'Clear Pyccd 1',icon='')
    toggle_pyccd_button2 = plots.make_button(False, 'Clear Pyccd 2',icon='')
    return_button = plots.make_button(False, 'Return to Sample', icon='')

    next_pt = plots.make_button(False, 'Next point', icon='')
    previous_pt = plots.make_button(False, 'Previous point', icon='')
    pyccd_button = plots.make_button(False, 'Run PyCCD 1', icon='')
    pyccd_button2 = plots.make_button(False, 'Run PyCCD 2', icon='')
    clear_layers = plots.make_button(False, 'Clear Map', icon='')

    delete_rows = plots.make_button(False, 'Delete Last',icon='')

    # Validate
    valid = plots.make_valid(False, 'Not Saved', '')
    b_valid = plots.make_valid(False, 'Not Saved', '') # TODO: DOes nothing/
    valid_load = plots.make_valid(False, 'Not Loaded','')

    # HTML
    pt_message = plots.make_html('<b>Current ID:</b>')
    time_label = plots.make_html('')
    coord_message = plots.make_html('Lat, Lon: ')
    selected_label = plots.make_html('ID of selected point')
    hover_label = plots.make_html('Test Value')
    text_brush = plots.make_html('Selected year range:')
    kml_link = plots.make_html('KML:')
    error_label = plots.make_html('Load a point')

    # Table
    table_widget = qgrid.show_grid(table, show_toolbar=False)


    ###### Plots ######

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
                             {}, {}, {}, colors=['black'], stroke_width=3,labels=['PyCCD Model'], display_legend=False)

    lc5 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x, 'y': lc2_y}, [1,1], {}, {},
                             {}, labels = ['Model Endpoint'], colors=['red'], marker='triangle-up')

    lc6 = plots.make_bq_plot('lines', [], [], {'x': lc1_x2, 'y': lc2_y2}, [1,1],
                             {}, {}, {}, colors=['black'], stroke_width=3, labels=['PyCCD Model'], display_legend=False)

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


    ###### Functions ######

    # Delete data highlighted in rows
    def delete_data_rows(a):
        measures.c.execute("DELETE FROM measures WHERE id = (SELECT MAX(id) FROM measures)")
        measures.change_table(0)
        condition = measures.break_check.value

        if condition == True:
            measures.sheet2.delete_row(2)
        else:
            measures.sheet.delete_row(2)


    # Reset dropdowns
    def reset_drops():

        measures.drop4.set_trait('options', ['Decision 4'])
        measures.drop5.set_trait('options', ['Decision 5'])
        measures.drop6.set_trait('options', ['Decision 6'])
        measures.drop7.set_trait('options', ['Decision 7'])
        measures.drop8.set_trait('options', ['Decision 8'])
        measures.veg_selector.disabled = True


    # Change dropdowns based on drop1 selection
    def drop1_clicked(selection):

        if selection.new == 'No':
            measures.drop2.set_trait('options', ['>30% Vegetated?','Yes', 'No'])
        elif selection.new == 'Yes':
            measures.drop2.set_trait('options', ['Ice/Snow'])
            measures.drop3.set_trait('options', ['No other information needed'])
            measures.reset_drops()


    # Change dropdowns based on drop2 selection
    def drop2_clicked(selection):

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


    # Change dropdowns based on drop3 selection
    def drop3_clicked(selection):

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


    # Change dropdowns based on drop4 selection
    def drop4_clicked(selection):

        if 'Trees?' in measures.drop4.options:
            if selection.new == 'Yes':
                measures.drop5.set_trait('options', ['Height >5m & Canopy >30%',
                                                     'Yes', 'No'])
            elif selection.new == 'No':
                measures.drop5.set_trait('options', ['Herbaceous Type',
                                                     'Grassland', 'Pasture',
                                                     'Row crops',
                                                     'Lawn/Urban Grass',
                                                     'Moss/Lichen'])


    # Change dropdowns based on drop5 selection
    def drop5_clicked(selection):

        if 'Height >5m & Canopy >30%' in measures.drop5.options:
            if selection.new == 'Yes':
                measures.drop6.set_trait('options', ['Forest Type', 'Evergreen',
                                                     'Deciduous', 'Mixed'])
                measures.drop7.set_trait('options', ['Leaf Type', 'Broad',
                                                     'Needle', 'Mixed',
                                                     'Unsure'])
                measures.drop8.set_trait('options', ['Location', 'Interior',
                                                     'Edge'])
            elif selection.new == 'No':
                measures.drop6.set_trait('options', ['Shrub Type', 'Evergreen',
                                                     'Deciduous', 'Mixed'])


    # Check validity of current sample
    def check_val_status(selection):

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


    # load the feature collection, database, and google sheet
    def load_everything(sender):

        measures.sheet = sheets.load_sheet(measures.spreadName.value, 0,  measures.spreadsheet.value)
        measures.sheet2 = sheets.load_sheet(measures.spreadName.value, 1,  measures.spreadsheet.value)
        measures.sheet3 = sheets.load_sheet(measures.spreadName.value, 2,  measures.spreadsheet.value)

        # Load the sample as a feature collection
        sample_path = measures.sampleWidget.value
        fc_df = utils.fc2dfgeo(sample_path)
        measures.fc_df, first_index = utils.check_id(fc_df)
        measures.valid_load.value = True
        measures.valid_load.description = 'Loaded!'
        measures.current_id = first_index


    # If the class type is 'break', turn on necessary widgets
    def turn_on_break_years(selection):

        if selection.new == 'Break':
            measures.break_years.disabled = False
            measures.break_year.disabled = False
        else:
            measures.break_years.disabled = True
            measures.break_year.disabled = True

    # If segment is stable, disable LCC direction and change agent
    def toggle_transitional_opts(selection):
        if selection.new == "Transitional":
            measures.direction.disabled = False
            measures.change_selector.disabled = False
            measures.change_other.disabled = False
            measures.ca_confidence.disabled = False
        elif selection.new == "Stable":
            measures.direction.disabled = True
            measures.change_selector.disabled = True
            measures.change_other.disabled = True
            measures.ca_confidence.disabled = True

    # Change yaxis for the sample time series
    def change_yaxis(value):

        measures.lc2_y.min = measures.ylim.value[0]
        measures.lc2_y.max = measures.ylim.value[1]


    # Change xaxis for the sample time series
    def change_xaxis(value):

        measures.lc1_x.min = datetime.date(measures.xlim.value[0], 2, 1)
        measures.lc1_x.max = datetime.date(measures.xlim.value[1], 2, 1)
        measures.year_range = [measures.xlim.value[0], measures.xlim.value[1]]


    # Change y axis for the clicked point
    def change_yaxis2(value):

        measures.lc2_y2.min = measures.ylim2.value[0]
        measures.lc2_y2.max = measures.ylim2.value[1]


    # Change x axis for the clicked point
    def change_xaxis2(value):

        measures.lc1_x2.min = datetime.date(measures.xlim2.value[0], 2, 1)
        measures.lc1_x2.max = datetime.date(measures.xlim2.value[1], 2, 1)


    # Display date of observation when hovering on scatterplot
    def hover_event(self, target):

        measures.hover_label.value = str(target['data']['x'])


    # Advance to next sample
    def advance(b):
        # TODO: Create a function that resets these values to avoid code redundancy
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
        measures.plot_ts(measures.lc2, 'ts')
        measures.plot_ts(measures.lc8, 'doy')
        measures.change_table(0)
        measures.valid.value = False
        measures.description='Not Saved'
        measures.notes.value='Enter any useful or interesting information about the land cover of this sample'
        measures.notes_seg_trend.value = 'Enter any useful or interesting information about the Time Trend of this sample'
        measures.notes_break.value = 'Enter any useful or interesting information about the Break in the time series'
        measures.break_check.value = False


    # Go to previous sample
    def decrease(b):

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
        #measures.plot_ts()
        measures.plot_ts(measures.lc2, 'ts')
        measures.plot_ts(measures.lc8, 'doy')
        measures.change_table(0)
        measures.valid.value = False
        measures.description='Not Saved'
        measures.notes.value='Enter any useful or interesting information about the land cover of this sample'
        measures.notes_seg_trend.value = 'Enter any useful or interesting information about the Time Trend of this sample'
        measures.notes_break.value = 'Enter any useful or interesting information about the Break in the time series'
        measures.break_check.value = False


    # Go to a specific sample
    def go_to_sample(b):

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
        #measures.plot_ts()
        measures.plot_ts(measures.lc2, 'ts')
        measures.plot_ts(measures.lc8, 'doy')
        measures.notes.value='Enter any useful or interesting information about the land cover of this sample'
        measures.notes_seg_trend.value = 'Enter any useful or interesting information about the Time Trend of this sample'
        measures.notes_break.value = 'Enter any useful or interesting information about the Break in the time series'
        measures.break_check.value = False

    # Return to sample location
    def return_to_sample(b):
        measures.map_point()

    # Update the table based on current ID
    def change_table(b):

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
        new_band = change['new']
        measures.y_ay1.label = new_band
        #measures.plot_ts()
        measures.plot_ts(measures.lc2, 'ts')
        measures.plot_ts(measures.lc8, 'doy')


    # Band selection for clicked point
    def on_band_selection2(change):
        new_band = change['new']
        band_index = change['owner'].index
        measures.band_index2 = band_index
        measures.lc3.x = measures.click_df['datetime']
        measures.lc3.y = measures.click_df[new_band]
        #measures.plot_ts(measures.lc3, 'ts')
        measures.y_ay2.label = new_band
        if measures.pyccd_flag2:
            measures.do_pyccd2(0)


    # Clear everything on map besides current sample
    def clear_map(b):

        lft.clear_map(measures.m, streets=True)
        if hasattr(measures, 'fc_df'):
            measures.map_point()


    # Add an image to the map when clicked on time series
    def add_image(self, target):

        m = measures.m
        df = measures.sample_df
        current_band = measures.band_list[measures.band_index1]
        sample_col = measures.sample_col
        stretch_min = measures.stretch_min.value
        stretch_max = measures.stretch_max.value
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
        stretch_min = measures.stretch_min.value
        stretch_max = measures.stretch_max.value
        b1 = measures.b1
        b2 = measures.b2
        b3 = measures.b3
        lft.click_event(target,m, current_band, df, sample_col, stretch_min, stretch_max,
                        b1, b2, b3)


    # Plot ts for point
    def do_draw(self, action, geo_json):
        
        current_band = measures.band_list[measures.band_index2]
        year_range = measures.year_range
        doy_range = measures.doy_range
        _col, _df = utils.handle_draw(action, geo_json, current_band, 
                                      year_range, doy_range)
        
        measures.click_geojson = geo_json
        measures.click_df = _df
        measures.click_col = _col
        
        # Disable ts collection checkbox but calculate box in the background
        
        measures.click_train.value = False
        measures.click_trainbox = utils.calculate_clicked_bbox(geo_json)

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


    # Add point location to map
    def map_point():
        zoom = int(measures.zoom_box.value)
        kml = measures.kml_link
        name = 'Sample point'
        measures.samplept_geojson = measures.fc_df['geometry'][measures.current_id]
        coord1 = measures.samplept_geojson['coordinates'][0]
        coord2 = measures.samplept_geojson['coordinates'][1]
        measures.coord_message.value = "Lat, Lon: {}, {}".format(coord2, coord1)
        lft.add_map_point(measures.samplept_geojson, zoom, measures.m, kml, name)


    # Get time series data for location.
    def get_ts():

        measures.error_label.value = 'Loading'
        coords = measures.fc_df['geometry'][measures.current_id]['coordinates']
        year_range = measures.year_range
        doy_range = measures.doy_range

        measures.current_band = measures.band_list[measures.band_index1]
        measures.sample_col = utils.get_full_collection(coords, year_range, doy_range)
        measures.sample_df = utils.get_df_full(measures.sample_col, coords).dropna()
        measures.error_label.value = 'Point Loaded!'

    # Add time series data to plots
    def plot_ts(plot, plottype):
        df = measures.sample_df

        if measures.color_check.value == True:
            color_marks = list(measures.sample_df['color'].values)
        else:
            color_marks = None

        band = measures.band_list[measures.band_index1]

        if plottype == 'ts':
            plots.add_plot_ts(df, plot, band=band, color_marks=color_marks)
        else:
            plots.add_plot_doy(df, plot, band=band, color_marks=color_marks)

        if measures.pyccd_flag:
            measures.do_pyccd(0)


    # Run pyccd for the sample location
    def do_pyccd(b):

        measures.pyccd_flag = True
        display_legend = measures.lc5.display_legend
        dfPyCCD = measures.sample_df
        band_index = measures.band_index1
        results = ccd_tools.run_pyccd(display_legend, dfPyCCD, band_index)
        if band_index > 5:
            measures.lc4.y = []
            measures.lc4.x = []
            measures.lc4.y = []
            measures.lc5.x = []
            measures.lc5.display_legend=False
            return
        else:
            ccd_tools.plot_pyccd(dfPyCCD, results, band_index,(0, 4000), measures.lc4, measures.lc5)
            measures.lc5.display_legend=True


    # Run pyccd for the clicked location
    def do_pyccd2(b):

        measures.pyccd_flag2 = True
        display_legend = measures.lc7.display_legend
        dfPyCCD = measures.click_df
        band_index = measures.band_index2
        results = ccd_tools.run_pyccd(display_legend, dfPyCCD, band_index)
        if band_index > 5:
            measures.lc6.y = []
            measures.lc6.x = []
            measures.lc7.y = []
            measures.lc7.x = []
            measures.lc7.display_legend=False
            return
        else:
            ccd_tools.plot_pyccd(dfPyCCD, results, band_index,(0, 4000), measures.lc6, measures.lc7)
            measures.lc7.display_legend=True

    # Clear pyccd results
    def clear_pyccd(b):
        measures.lc4.x = []
        measures.lc5.y = []

    def clear_pyccd2(b):
        measures.lc6.x = []
        measures.lc7.y = []

    # Save sample
    def save_sample():
        # Connect to the database
        #conn = sqlite3.connect(measures.dbPath)
        #c = conn.cursor()

        # Get everything in right format
        year1 = measures.years.value[0]
        year2 = measures.years.value[1]

        waterType = 'N/A'
        bareType = 'N/A'
        albedo = 'N/A'
        use = 'N/A'
        height = 'N/A'
        transport = 'N/A'
        impervious = 'N/A'
        density = 'N/A'
        vegType1 = 'N/A'
        seg_notes = 'N/A'
        herbaceousType = 'N/A'
        shrubType = 'N/A'
        forestPhenology = 'N/A'
        leafType = 'N/A'
        b_notes_value = 'N/A'
        b_changeAgent = 'N/A'
        b_ca_other = 'N/A'
        b_confCA = 'N/A'
        b_direction = 'N/A'
        location = 'N/A'

        coverType = measures.drop0.value

        # Segment type
        seg_type = measures.drop9.value
        direction = measures.direction.value
        direction = [str(i) for i in direction]
        direction = ', '.join(direction)

        changeAgent = measures.change_selector.value
        changeAgent = [str(i) for i in changeAgent]
        changeAgent = ', '.join(changeAgent)
        confCA = measures.ca_confidence.value
        ca_other = measures.change_other.value

        if ca_other == 'Specify other':
            ca_other = 'N/A'
        seg_notes = measures.notes_seg_trend.value

        # Break
        condition = measures.break_check.value
        if condition:
            condition = 'Break'
        else:
            condition = 'No Break'
        b_changeAgent = measures.b_change_selector.value
        b_changeAgent = [str(i) for i in b_changeAgent]
        b_changeAgent = ', '.join(b_changeAgent)
        break_year = measures.break_year.value
        break_range1 = measures.break_years.value[0]
        break_range2 = measures.break_years.value[1]
        b_confCA = measures.b_ca_confidence.value
        b_ca_other = measures.b_change_other.value

        if b_ca_other == 'Specify other':
            b_ca_other = 'N/A'

        b_direction = measures.b_direction.value
        b_direction = [str(i) for i in b_direction]
        b_direction = ', '.join(b_direction)

        class1 = 'Unfilled'

        # Ice/Snow
        if measures.drop1.value == 'Yes':
            class1 = 'Snow/Ice'
        else:
            if measures.drop2.value == 'No': #Non-Veg
                class1 = measures.drop3.value
                if class1 == 'Water':
                    waterType = measures.drop4.value
                elif class1 == 'Bare':
                    bareType = measures.drop4.value
                else:
                    albedo = measures.drop4.value #HERE
                    use = measures.drop5.value
                    height = measures.drop6.value
                    transport = measures.drop7.value
                    impervious = measures.drop8.value
            elif measures.drop2.value == 'Yes': #Veg
                density = measures.drop3.value
                vegType1 = measures.veg_selector.value
                vegType1 = [str(i) for i in vegType1]
                vegType1 = ', '.join(vegType1)
                if measures.drop4.value == 'No': #Herbaceous
                    class1 = 'Herbaceous'
                    herbaceousType = measures.drop5.value
                elif measures.drop4.value == 'Yes':
                    class1 = 'Forest'
                    forestPhenology = measures.drop6.value
                    leafType = measures.drop7.value
                    location = measures.drop8.value

        conf = measures.confidence.value
        notes_value = measures.notes.value
        b_notes_value = measures.notes_break.value

        # Get coordinates depending on source
        if measures.click_train:
            idSample = 0
            lat = measures.click_geojson['geometry']['coordinates'][1]
            lon = measures.click_geojson['geometry']['coordinates'][0]
        else:
            idSample = measures.current_id
            lat = measures.samplept_geojson['coordinates'][1]
            lon = measures.samplept_geojson['coordinates'][0]


        sampleInput = (idSample, lat, lon, year1, year2, coverType, condition,
                       class1, waterType, bareType, albedo, use, height,
                       transport, impervious, density, vegType1,
                       herbaceousType, shrubType, forestPhenology, leafType,
                       location, conf, notes_value, seg_type, direction,
                       changeAgent, confCA, ca_other, seg_notes,
                       break_year, break_range1, break_range2)

        # Put sample information into database
        #c.execute("""insert into measures
        #          values {i}""".format(i=sampleInput))
        #
        # Save (commit) the changes
        #conn.commit()

        # Close the cursor
        #c.close()


        # Save to drive
        sampleInputList = [str(idSample), str(lat), str(lon), str(year1),
                           str(year2), coverType, condition,
                           class1, waterType, bareType, albedo,
                           use, height, transport, impervious, density,
                           vegType1, herbaceousType, shrubType,
                           forestPhenology, leafType, location, str(conf),
                           notes_value, seg_type, direction, changeAgent,
                           str(confCA), ca_other, seg_notes]

        sampleInputListFull = sampleInputList

        # Save break information to second sheet
        if condition == 'Break':
            breakList = [str(idSample), str(lat), str(lon), b_changeAgent,
                         b_ca_other, b_confCA, break_year, break_range1,
                         break_range2, b_direction, b_notes_value]
            count = len(measures.sheet2.col_values(1))
            measures.sheet2.insert_row(breakList, 2)
            time.sleep(3)
            count_new = len(measures.sheet2.col_values(1))
        elif measures.click_train:
            count = len(measures.sheet3.col_values(1))
            measures.sheet3.insert_row(sampleInputListFull, 2)
            count_new = len(measures.sheet3.col_values(1))
        else:
            count = len(measures.sheet.col_values(1))
            measures.sheet.insert_row(sampleInputListFull, 2)
            time.sleep(3)
            count_new = len(measures.sheet.col_values(1))

        if count_new > count:
            # Change save validity state
            if condition == 'Break':
                measures.b_valid.value = True
                measures.b_valid.description='Saved!'
            else:
                measures.valid.value = True
                measures.valid.description='Saved!'
            measures.reset_everything()
        else:
            time.sleep(10)
            if condition == 'Break':
                count_new = len(measures.sheet2.col_values(1))
            else:
                count_new = len(measures.sheet.col_values(1))
            if count_new > count:
                # Change save validity state
                measures.valid.value = True
                measures.valid.description='Saved!'
                measures.reset_everything()

    # Reset all widgets
    def reset_everything():
        
        measures.click_train.set_trait('value', False)
        measures.drop1.set_trait('value', 'Persistant Ice?')
        measures.drop2.set_trait('options', ['Decision 3'])
        measures.drop3.set_trait('options', ['Decision 4'])
        measures.drop5.set_trait('options', ['Decision 5'])
        measures.drop6.set_trait('options', ['Decision 6'])
        measures.drop7.set_trait('options', ['Decision 7'])
        measures.drop8.set_trait('options', ['Decision 8'])
        measures.veg_selector.disabled = True
        measures.years.set_trait('value',[1990, 1991])
        measures.confidence.set_trait('value',0)
        measures.ca_confidence.set_trait('value',0)

    # Interaction function for saving sample
    def do_save_sample(b):
        measures.save_sample()
       #measures.change_table(0)
        measures.reset_everything()

    # Activate break widgets
    def do_activate_break(b):
        if b.new:
            measures.break_year.disabled = False
            measures.break_years.disabled = False
            measures.b_direction.disabled = False
            measures.b_change_selector.disabled = False
            measures.b_change_other.disabled = False
            measures.b_ca_confidence.disabled = False
            measures.notes_break.disabled = False
            measures.b_save_button.disabled = False
        else:
            measures.b_save_button.disabled = True
            measures.break_year.disabled = True
            measures.break_years.disabled = True
            measures.b_direction.disabled = True
            measures.b_change_selector.disabled = True
            measures.b_change_other.disabled = True
            measures.b_ca_confidence.disabled = True
            measures.notes_break.disabled = True
    
    # Enable collection of TS box as training data
    def enable_ts_collection(b):
        if b.new:
            measures.box_geojson = ipyleaflet.GeoJSON(data=measures.click_trainbox.getInfo(),
                                             style={'color': 'black'},
                                             name='TS train box')
            measures.m.add_layer(measures.box_geojson) 
        else:
            measures.m.remove_layer(measures.box_geojson)

    ####### Widget Interactions #######

    click_train.observe(enable_ts_collection, 'value')
    break_check.observe(do_activate_break, 'value')
    delete_rows.on_click(delete_data_rows)
    return_button.on_click(return_to_sample)
    save_button.on_click(do_save_sample)
    b_save_button.on_click(do_save_sample)
    validate.on_click(check_val_status)
    drop1.observe(drop1_clicked, 'value')
    drop2.observe(drop2_clicked, 'value')
    drop3.observe(drop3_clicked, 'value')
    drop4.observe(drop4_clicked, 'value')
    drop5.observe(drop5_clicked, 'value')
    drop9.observe(toggle_transitional_opts, 'value')

    load_button.on_click(load_everything)

    dc = ipyleaflet.DrawControl(marker={'shapeOptions': {'color': '#ff0000'}},
                                polygon={}, circle={}, circlemarker={},
                                polyline={})

    zoom = 5
    layout = widgets.Layout(width='50%')
    center = (3.3890701010382958, -67.32297252983098)
    m = lft.make_map(zoom, layout, center)
    lft.add_basemap(m, ipyleaflet.basemaps.Esri.WorldImagery)

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

    # Samples
    next_pt.on_click(advance)
    previous_pt.on_click(decrease)

    # pyccd
    pyccd_button.on_click(do_pyccd)
    pyccd_button2.on_click(do_pyccd2)
    toggle_pyccd_button.on_click(clear_pyccd)
    toggle_pyccd_button2.on_click(clear_pyccd2)

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

