# Functions for interacting with pyccd

import ccd
import numpy as np
import datetime

# Plot pyccd results for pixel
def plot_pyccd(dfPyCCD, results, band, yl, scatter_ts, scatter_ts_breaks):

    dates = np.array(dfPyCCD['ord_time'])
    blues = np.array(dfPyCCD['BLUE'])
    greens = np.array(dfPyCCD['GREEN'])
    reds = np.array(dfPyCCD['RED'])
    nirs = np.array(dfPyCCD['NIR'])
    swir1s = np.array(dfPyCCD['SWIR1'])
    swir2s = np.array(dfPyCCD['SWIR2'])
    thermals = np.array(dfPyCCD['THERMAL'])
    qas = np.array(dfPyCCD['pixel_qa'])

    band_names = ['Blue SR', 'Green SR', 'Red SR', 'NIR SR', 'SWIR1 SR', 'SWIR2 SR','THERMAL']
    plotlabel = band_names[band]

    plot_arrays = [blues, greens, reds, nirs, swir1s, swir2s]
    plotband = plot_arrays[band]

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

    break_y = [plotband[dates == i][0] for i in break_dates]

    break_dates_plot = [datetime.datetime.fromordinal(i).strftime('%Y-%m-%d %H:%M:%S.%f') for i in break_dates]


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

    scatter_ts.x = _x
    scatter_ts.y = _y
    scatter_ts_breaks.x = np.array(break_dates_plot, dtype='datetime64')
    scatter_ts_breaks.y = break_y

# Run pyccd for a pixel
def run_pyccd(display_legend, dfPyCCD, band_index):

    display_legend=True

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

    return results
