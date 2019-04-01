# measures_collector
Tool to collect training and reference data for the measures project at Boston
University. 

In order to use the Google Earth Engine API you need to have an active account.
Check the installation instructions to set up the environment and authentication
credentials.

Widget and map interaction should work right away with a classic jupyter notebook.
In order to use them with a JupyterLab notebook, four extensions are required. 
They can be installed with the commands below.

- `jupyter labextension install jupyter-leaflet`
- `jupyter labextension install @jupyter-widgets/jupyterlab-manager`
- `jupyter labextension install bqplot`
- `jupyter labextension install qgrid`

If you're interested in a simple visualization tool that shows time series
and pyccd models, check [https://github.com/parevalo/tstools-online].
