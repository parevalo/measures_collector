# tstools_online
Visualize time series obtained from Google Earth Engine and run pyccd on them

In order to use the Google Earth Engine API you need to have an active account
and set up authentication credentials as described [here](https://developers.google.com/earth-engine/python_install_manual).

Widget and map interaction should work right away with a classic jupyter notebook.
In order to use them with a JupyterLab notebook, three extensions are required. 
They can be installed with the commands below.

- `jupyter labextension install jupyter-leaflet`
- `jupyter labextension install @jupyter-widgets/jupyterlab-manager`
- `jupyter labextension install bqplot`


The second extension requires [nodejs](https://nodejs.org/en/).

