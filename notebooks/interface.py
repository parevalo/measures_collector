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
import os

# Google sheets API
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Turn off pandas warning
pd.options.mode.chained_assignment = None

# Configure the pretty printing output.
pp = pprint.PrettyPrinter(depth=4)


class interface(object):
    """A class to hold interface for defining sample attributes"""

    def fc2dfgeo(fc):
        # Convert a FeatureCollection into a pandas DataFrame
        # Features is a list of dict with the output
        features = fc.getInfo()['features']

        dictarr = []

        for f in features:
            # Store all attributes in a dict
            attr = f['properties']
            # and treat geometry separately
            attr['geometry'] = f['geometry']
            dictarr.append(attr)

        df = geopandas.GeoDataFrame(dictarr)
        return df


    # Set up database
    current_id = 0
    dbPath = os.getcwd() + '/sample_database_4'
    if not os.path.isfile(dbPath):
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        c.execute('''CREATE TABLE sample4
                 (id text, lat text, lon text, year1 text, year2 text, condition text, change text,
                 class text, water text, bare text, albedo text, use text,
                 height text, transport text, impervious text, density text,
                 vegType1 text, herbaceous text, shrub text, forestPhenology text,
                 leafType text, location text, confidence real, notes text)''')
        print('Database created')


    # Create widgets
    # Years slider
    years = widgets.IntRangeSlider(value=[2012, 2015], min=1990, max=2018,
            step=1, description='Years:', disabled=False, continuous_update=False,
            orientation='horizontal', readout=True, readout_format='d')

    # Dropdown hierachy
    drop1 = widgets.Dropdown(options=['Persistant Ice?','Yes', 'No'],
                value='Persistant Ice?', description='Decision 1', disabled=False)

    drop2 = widgets.Dropdown(options=['Decision 2'],
                value='Decision 2', description='Decision 2', disabled=False)

    drop3 = widgets.Dropdown(options=['Decision 3'],
                value='Decision 3', description='Decision 3', disabled=False)

    drop4 = widgets.Dropdown(options=['Decision 4'],
                value='Decision 4', description='Decision 4', disabled=False)

    drop5 = widgets.Dropdown(options=['Decision 5'],
                value='Decision 5', description='Decision 5', disabled=False)

    drop6 = widgets.Dropdown(options=['Decision 6'],
                value='Decision 6', description='Decision 6', disabled=False)

    drop7 = widgets.Dropdown(options=['Decision 7'],
                value='Decision 7', description='Decision 7', disabled=False)
    drop8 = widgets.Dropdown(options=['Decision 8'],
                value='Decision 8', description='Decision 8', disabled=False)

    drop9 = widgets.Dropdown(options=['Select Label','Stable','Transitional','Break'],
                value='Select Label', description='Label Type:', disabled=False)
    veg_selector = widgets.SelectMultiple(
                        options=['Veg Type','Cropland', 'Plantation', 'Wetland', 'Riparian/Flood'],
                        value=['Veg Type'],
                        description='Veg Type:',
                        disabled=True
                      )

    change_selector = widgets.SelectMultiple(
                        options=['None','Deforestation/Logging', 'Fire', 'Insect damage', 'Urban Dev.',
                                'Flooding','Decline/Degradation','Regrowth','Riparian/Water shift','Other (Specify)'],
                        value=['None'],
                        # rows=10,
                        description='Change Agent:',
                        disabled=False
                      )
    change_other = widgets.Text(value='Specify other',
                    placeholder='Specify other', description='Other:',
                    disabled=False, continuous_update=True)

    # Break versus transitional check box
    break_cb = widgets.Checkbox(
                    value=False,
                    description='Break Label?',
                    disabled=False
    )
    break_years = widgets.IntRangeSlider(value=[2012, 2015], min=1990, max=2018,
                    step=1, description='Break Years:', disabled=True, continuous_update=False,
                    orientation='horizontal', readout=True, readout_format='d')

    # Display current validity of sample
    valid = widgets.Valid(value=False, description='Not Saved', readout='')


    # Create button for checking validity
    validate = widgets.Button(value=False, description='Validate', disabled=False,
                button_style='', icon='check')

    # Save the current sample, only possible when validity has been approved
    save_button = widgets.Button(value=False, description='Save', disabled=False,
                button_style='')

    # Load everything
    load_button = widgets.Button(value=False, description='Load', disabled=False,
                button_style='')

    valid_load = widgets.Valid(value=False, description='Not Loaded', readout='')

    # Interpreters confidence
    confidence = widgets.IntSlider(value=0, min=0, max=3, step=1, description='Confidence:',
                    disabled=False, continuous_update=False, orientation='horizontal',
                    readout=True, readout_format='d')

    # Notes
    notes = widgets.Textarea(value='Enter any useful or interesting information about the sample.',
                    placeholder='Enter any useful or interesting information about the sample',
                    description='Notes:', layout=widgets.Layout(width='70%'), disabled=False)

    # Spreadsheet information
    spreadsheet = widgets.Text(value='Google Spreadsheet Credential JSON',
                    placeholder='Google Spreadsheet Credential JSON',
                    description='Credentials:',disabled=False,
                    continuous_update=True)

    # MEaSUREs_ELB
    spreadName = widgets.Text(value='Google Spreadsheet Name',
                    placeholder='Google Spreadsheet Name', description='Name:',
                    disabled=False, continuous_update=True)
    # Sample path
    sampleWidget = widgets.Text(value='Path to sample feature collection',
                description='Path:',
                disabled=False, continuous_update=True)
    def __init__(self):
        interface.sample_path = None
        interface.sheet = None
    def reset_drops():
        interface.drop4.set_trait('options', ['Decision 4'])
        interface.drop5.set_trait('options', ['Decision 5'])
        interface.drop6.set_trait('options', ['Decision 6'])
        interface.drop7.set_trait('options', ['Decision 7'])
        interface.drop8.set_trait('options', ['Decision 8'])
        interface.veg_selector.disabled = True

    def drop1_clicked(selection):
        """ Generate secondary class selector after initial class is chosen """
        if selection.new == 'No':
            interface.drop2.set_trait('options', ['>30% Vegetated?','Yes', 'No'])
        elif selection.new == 'Yes':
            interface.drop2.set_trait('options', ['Ice/Snow'])
            interface.drop3.set_trait('options', ['No other information needed'])
            interface.reset_drops()

    def drop2_clicked(selection):
        """ Generate vegetation class information after initial class is chosen """
        if '>30% Vegetated?' in interface.drop2.options:
            if selection.new == 'Yes':
                interface.drop3.set_trait('options', ['Density','Closed (60-70%)', 'Open (30-60%)', 'Sparse (<30%)'])
                interface.veg_selector.disabled = False
                interface.drop4.set_trait('options', ['Trees?','Yes', 'No'])

            elif selection.new == 'No':
                interface.drop3.set_trait('options', ['Dominant Cover?', 'Water','Bare','Developed'])
                interface.drop4.set_trait('options', ['Decision 4'])
                interface.drop5.set_trait('options', ['Decision 5'])
                interface.drop6.set_trait('options', ['Decision 6'])
                interface.drop7.set_trait('options', ['Decision 7'])
                interface.drop8.set_trait('options', ['Decision 8'])
                interface.veg_selector.disabled = True

        else:
            interface.drop3.set_trait('options', ['No Other Information Needed'])

    def drop3_clicked(selection):
        """ Generate third class selector after initial class is chosen """
        if 'Dominant Cover?' in interface.drop3.options:
            interface.veg_selector.disabled = True
            if selection.new == 'Water':
                interface.drop4.set_trait('options', ['Water Type','Shore/Inter tidal', 'Shallows', 'River','Lake/Reservoir','Ocean'])
            elif selection.new == 'Bare':
                interface.drop4.set_trait('options', ['Bare Type', 'Soil','Rock','Quarry (Active)','Beach/Sand'])
            elif selection.new == 'Developed':
                interface.drop4.set_trait('options', ['Surface Albedo', 'High','Low','Mixed'])
                interface.drop5.set_trait('options', ['Use','Residential', 'Commercial/Industrial'])
                interface.drop6.set_trait('options', ['Building Height','No Buildings','1-2 Stories', '3-5 Stories','5+ Stories'])
                interface.drop7.set_trait('options', ['Transport','Road','Not Applicable'])
                interface.drop8.set_trait('options', ['% Impervious','High (60-100)','Medium (30-60)','Low (<30)'])

    def drop4_clicked(selection): # ERIC HERE
        """ Generate fourth class selector after initial class is chosen """
        if 'Trees?' in interface.drop4.options:
            if selection.new == 'Yes':
                interface.drop5.set_trait('options', ['Height >5m & Canopy >30%','Yes', 'No'])
            elif selection.new == 'No':
                interface.drop5.set_trait('options', ['Herbaceous Type','Grassland', 'Pasture','Lawn/Urban Grass','Moss/Lichen'])


    def drop5_clicked(selection):
        """ Generate fifth class selector after initial class is chosen """
        if 'Height >5m & Canopy >30%' in interface.drop5.options:
            if selection.new == 'Yes':
                interface.drop6.set_trait('options', ['Forest Type','Evergreen', 'Deciduous','Mixed'])
                interface.drop7.set_trait('options', ['Leaf Type','Broad', 'Needle','Unsure'])
                interface.drop8.set_trait('options', ['Location','Interior', 'Edge'])

            elif selection.new == 'No':
                interface.drop6.set_trait('options', ['Shrub Type','Evergreen', 'Deciduous','Mixed'])


    def check_val_status(selection):
        """ Check the validity of the current sample and change valid widget accordingly """
        selected_secondary_lc = False
        wrote_correct_lc = False
        if interface.second_class_drop.value != 'Secondary Class Information':
            selected_secondary_lc = True
        else:
            print("Must specify secondary class information!")
        if interface.lc.value.capitalize() == interface.textClass.value.capitalize():
            wrote_correct_lc = True
        if selected_secondary_lc and wrote_correct_lc:
            interface.valid.value = True
            interface.save_button.disabled = False

    def load_everything(sender):
        # Load Google Spreadsheet and GEE Feature Collection
        scope = ['https://spreadsheets.google.com/feeds' + ' ' +'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(interface.spreadsheet.value, scope)
        client = gspread.authorize(creds)
        interface.sheet = client.open(interface.spreadName.value).sheet1
        interface.sample_path = ee.FeatureCollection(interface.sampleWidget.value)
        interface.fc_df = interface.fc2dfgeo(interface.sample_path)
        if 'ID' not in interface.fc_df.columns:
            first_index = interface.fc_df.index.min()
            interface.fc_df['ID'] = interface.fc_df.index
        else:
            first_index = interface.fc_df['ID'].min()
        interface.fc_df = interface.fc_df.set_index('ID')
        interface.valid_load.value = True
        interface.valid_load.description='Loaded!'
        interface.current_id = first_index - 1

    def turn_on_break_years(a):
        if interface.break_years.disabled == True:
            interface.break_years.disabled = False
        else:
            interface.break_years.disabled = True

    # Handle widget interactions
    # Call function check_val_status when button is clicked
    validate.on_click(check_val_status)
    # Primary class selector action
    drop1.observe(drop1_clicked, 'value')
    # Secondary class selector action
    drop2.observe(drop2_clicked, 'value')
    # Third class selector action
    drop3.observe(drop3_clicked, 'value')
    drop4.observe(drop4_clicked, 'value')
    drop5.observe(drop5_clicked, 'value')

    break_cb.observe(turn_on_break_years)

    # Load database and sample
    load_button.on_click(load_everything)

