import ipywidgets as widgets
import bqplot, qgrid

# Functions for generating widgets

# Return an integer range slider widget
def make_range_slider(value, _min, _max, step, description, disabled=False,
                      continuous_update=False, orientation='horizontal',
                      readout=True, readout_format='d'):

    widg = widgets.IntRangeSlider(value=value, min=_min, max=_max,
                                  description=description, disabled=disabled,
                                  continuous_update=continuous_update,
                                  orientation=orientation, readout=readout,
                                  readout_format=readout_format)
    return widg

# Return a normal slider
def make_slider(value, _min, _max, step, description, disabled=False,
                      continuous_update=False, orientation='horizontal',
                      readout=True, readout_format='d'):

    widg = widgets.IntSlider(value=value, min=_min, max=_max,
                            description=description, disabled=disabled,
                            continuous_update=continuous_update,
                            orientation=orientation, readout=readout,
                            readout_format=readout_format)
    return widg

# Return a dropdown selection widget
def make_drop(value, options, description, disabled=False):

    widg = widgets.Dropdown(options=options, value=value,
                            description=description, disabled=disabled)

    return widg

# Return a select multiple widget
def make_selector(value, options, description, disabled=False):

    widg = widgets.SelectMultiple(options=options,value=value,
                                  description=description, disabled=disabled)

    return widg

# Return a textbox widget
def make_text(value, placeholder, description, disabled=False, continuous_update=True):

    widg = widgets.Text(value=value, placeholder=placeholder, disabled=disabled,
                         continuous_update=continuous_update)

    return widg

# Return a textbox floating integer widget
def make_text_float(value, placeholder, description, disabled=False, continuous_update=True):

    widg = widgets.FloatText(value=value, placeholder=placeholder, description=description, disabled=disabled,
                         continuous_update=continuous_update)

    return widg

# Return a large textbox
def make_text_large(value, description, placeholder, layout=None,
                    disabled=False, continuous_update=True):

    widg = widgets.Textarea(value=value, placeholder=placeholder, disabled=disabled,
                            description=description, continuous_update=continuous_update,
                            layout=layout)

    return widg

# Return a validaty check widget
def make_valid(value, description, readout):

    widg = widgets.Valid(value=value, description=description, readout=readout)

    return widg

# Return a checkbox widget
def make_checkbox(value, description, disabled=False):

    widg = widgets.Checkbox(value=value, description=description, dsiabled=False)

    return widg

# Return a button widget
def make_button(value, description, disabled=False, icon='check'):

    widg = widgets.Button(value=value, description=description, disabled=disabled,
                          icon=icon)

    return widg

# Make an HTML widget
def make_html(text):

    widg = widgets.HTML(text)

    return widg

# Make pqplot plot
def make_bq_plot(plot_type, x, y, scales, size, interactions, selected_style, unselected_style,
                 display_legend=False, labels = [''], colors=['#43a2ca'], stroke_width=3, marker='circle'):

    if plot_type == 'scatter':
        chart = bqplot.Scatter(x=x, y=x, scales=scales, size=size, interactions=interactions,
                               selected_style=selected_style, unselected_style=unselected_style,
                               display_legend=display_legend, labels=labels, marker=marker,colors=colors)
    elif plot_type == 'lines':
        chart = bqplot.Lines(x=x, y=y, colors=colors, stroke_width=stroke_width, scales=scales,
                             size=size)

    return chart

# Make bqplot figure
def make_bq_figure(marks, axes, layout, title):

    fig = bqplot.Figure(marks=marks, axes=axes, layout=layout, title=title)

    return fig

# Make bqplot axis
def make_bq_axis(label, scale, num_ticks=None, tick_format=None, orientation=None):

    ax = bqplot.Axis(label=label, scale=scale)

    if num_ticks is not None:
        ax.num_ticks = num_ticks

    if tick_format is not None:
         ax.tick_format = tick_format

    if orientation is not None:
         ax.orientation = orientation


    return ax

# Make bqplot scale
def make_bq_scale(scale_type, _min, _max):

    if scale_type == 'linear':
        scale = bqplot.LinearScale(min=_min, max=_max)
    elif scale_type == 'date':
        scale = bqplot.DateScale(min=_min, max=_max)

    return scale

# Make a table widget
def make_table(table, show_toolbar=False):

    table = qgrid.show_grid(table, show_toolbar=show_toolbar)

    return table

# Add time series to plot
def add_plot_ts(df, plot, band='SWIR1', color_marks=None):

    plot.x = df['datetime']
    plot.y = df[band]
    if color_marks is not None:
        plot.colors = list(df['color'].values)
    else:
        plot.colors = ['#43a2ca']

def add_plot_doy(df, plot, band='SWIR1', color_marks=None):

    plot.x = df['doy']
    plot.y = df[band]
    if color_marks is not None:
        plot.colors = list(df['color'].values)
    else:
        plot.colors = ['#43a2ca']
