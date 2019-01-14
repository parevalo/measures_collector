# Functions specific for measures notebook

# Dropdown actions
def drop1_clicked(selection, drop2, drop3):
    """ Generate secondary class selector after initial class is chosen """
    if selection.new == 'No':
        drop2.set_trait('options', ['>30% Vegetated?','Yes', 'No'])
    elif selection.new == 'Yes':
        drop2.set_trait('options', ['Ice/Snow'])
        drop3.set_trait('options', ['No other information needed'])

# Change other dropdowns based on selection of drop2
def drop2_clicked(selection, drop2, drop3, drop4, drop5, drop6, drop7, drop8, veg_selector):
    if '>30% Vegetated?' in drop2.options:
        if selection.new == 'Yes':
            drop3.set_trait('options', ['Density','Closed (60-70%)', 'Open (30-60%)', 'Sparse (<30%)'])
            veg_selector.disabled = False
            drop4.set_trait('options', ['Trees?','Yes', 'No'])
        elif selection.new == 'No':
            drop3.set_trait('options', ['Dominant Cover?', 'Water','Bare','Developed'])
            drop4.set_trait('options', ['Decision 4'])
            drop5.set_trait('options', ['Decision 5'])
            drop6.set_trait('options', ['Decision 6'])
            drop7.set_trait('options', ['Decision 7'])
            drop8.set_trait('options', ['Decision 8'])
            veg_selector.disabled = True

    else:
        drop3.set_trait('options', ['No Other Information Needed'])

# Change other dropdowns based on selection of drop3
def drop3_clicked(selection, drop3, drop4, drop5, drop6, drop7, drop8, veg_selector):
    if 'Dominant Cover?' in drop3.options:
        veg_selector.disabled = True
        if selection.new == 'Water':
            drop4.set_trait('options', ['Water Type','Shore/Inter tidal', 'Shallows', 'River','Lake/Reservoir','Ocean'])
        elif selection.new == 'Bare':
            drop4.set_trait('options', ['Bare Type', 'Soil','Rock','Quarry (Active)','Beach/Sand'])
        elif selection.new == 'Developed':
            drop4.set_trait('options', ['Surface Albedo', 'High','Low','Mixed'])
            drop5.set_trait('options', ['Use','Residential', 'Commercial/Industrial'])
            drop6.set_trait('options', ['Building Height','No Buildings','1-2 Stories', '3-5 Stories','5+ Stories'])
            drop7.set_trait('options', ['Transport','Road','Not Applicable'])
            drop8.set_trait('options', ['% Impervious','High (60-100)','Medium (30-60)','Low (<30)'])

# Change other dropdowns based on selection of drop4
def drop4_clicked(selection, drop4, drop5):
    if 'Trees?' in drop4.options:
        if selection.new == 'Yes':
            drop5.set_trait('options', ['Height >5m & Canopy >30%','Yes', 'No'])
        elif selection.new == 'No':
            drop5.set_trait('options', ['Herbaceous Type','Grassland', 'Pasture','Lawn/Urban Grass','Moss/Lichen'])

# Change other dropdowns based on selection of drop5
def drop5_clicked(selection, drop5, drop6, drop7, drop8):
    if 'Height >5m & Canopy >30%' in drop5.options:
        if selection.new == 'Yes':
            drop6.set_trait('options', ['Forest Type','Evergreen', 'Deciduous','Mixed'])
            drop7.set_trait('options', ['Leaf Type','Broad', 'Needle','Unsure'])
            drop8.set_trait('options', ['Location','Interior', 'Edge'])
        elif selection.new == 'No':
            drop6.set_trait('options', ['Shrub Type','Evergreen', 'Deciduous','Mixed'])


# Check the validity of the current sample and change valid widget accordingly
def check_val_status(selection, lc, textClass, second_class_drop, valid, save_button):
    selected_secondary_lc = False
    wrote_correct_lc = False
    if second_class_drop.value != 'Secondary Class Information':
        selected_secondary_lc = True
    else:
        print("Must specify secondary class information!")
    if lc.value.capitalize() == textClass.value.capitalize():
        wrote_correct_lc = True
    if selected_secondary_lc and wrote_correct_lc:
        valid.value = True
        save_button.disabled = False

# Turn on widgets for break information
def turn_on_break_years(selection):
    if selection.new == 'Break':
        break_years.disabled = False
        break_year.disabled = False
    else:
        break_years.disabled = True
        break_year.disabled = True

# Reset dropdown selectors
def reset_drops(drop4, drop5, drop6, drop7, drop8, veg_selector):
    drop4.set_trait('options', ['Decision 4'])
    drop5.set_trait('options', ['Decision 5'])
    drop6.set_trait('options', ['Decision 6'])
    drop7.set_trait('options', ['Decision 7'])
    drop8.set_trait('options', ['Decision 8'])
    veg_selector.disabled = True
