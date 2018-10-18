# Step 1: Clone repo

`git clone https://github.com/parevalo/tstools_online.git`

# Step 2: Get anaconda or miniconda

Make sure conda is installed, either from Anaconda or Miniconda.
You can get miniconda [here](https://conda.io/miniconda.html).
If you already have it installed, skip to the next step.

# Step 3: Create a conda environment

Locate the newly created folder and the requirements.yml file. Then
create a new conda environment specifying the name you want (e.g. tst_online).

`conda env create -n tst_online -f requirements.yml`

The newly created environment will contain all the requirements, including
the Google Earth Engine (GEE) API and its dependencies.

Activate the conda environment: `source activate tst_online`

# Step 4: Set up GEE credentials

Set up the credentials using the following command:
`python -c "import ee; ee.Initialize()"`

If no credentials are found (if you've never done this before)
an error will appear with the instructions on how to create the
new credentials. The steps involve opening a web page where
you must sign in with the Google Account associated with GEE.
You will authorize access and the page will provide an
authorization code. You will copy and paste it in the terminal where
the script is running. More details can be found 
[here.](https://developers.google.com/earth-engine/python_install_manual#setting-up-authentication-credentials)

# Step 5: Test the GEE installation

In a Python session, run the following code:

```
# Import the Earth Engine Python Package
import ee

# Initialize the Earth Engine object, using the authentication credentials.
ee.Initialize()

# Print the information for an image asset.
image = ee.Image('srtm90_v4')
print(image.getInfo())
```

You should se the metadata for an image

# Step 6: Run the notebook

Start a jupyter notebook and open the notebook you need

`jupyter notebook`

