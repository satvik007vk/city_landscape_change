# City Landscape Change

Comparing landscape and environmental change across cities over time using Google Earth Engine (GEE) data.

## Setup

This project uses [`uv`](https://docs.astral.sh/uv/getting-started/installation/) to manage Python and its dependencies.

- Make sure `uv` and Python 3.12 or newer are installed in your machine.
- Run `uv sync` to install the project's dependencies.

## Running the analyses

The Google Earth Engine (GEE) Python API requires a Google account registered for Earth Engine access. The first time you run the notebook, it will open a browser window asking you to sign in and authorize access; this only needs to happen once per machine.

Open and run the jupyter notebook `src/analyses/analyses.ipynb`for all analyses.

## Analyse your custom Area of Interest (AOI)

Follow the steps below to run the analyses for a custom area:

1. Get a boundary for your city of interest as a GeoJSON file.
2. Save it as `data/{CityName}_boundary.geojson`, where `{CityName}` is the name you want to use for your city (e.g. `data/Rotterdam_boundary.geojson`).
3. In `src/analyses/analyses.ipynb`, set `CITY_NAME` to that same name (e.g. `CITY_NAME = "Rotterdam"`) and run the notebook as usual.