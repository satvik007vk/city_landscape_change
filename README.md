# City Landscape Change

Comparing landscape and environmental change across cities over time using Google Earth Engine (GEE) data.

## Setup

This project uses [`uv`](https://docs.astral.sh/uv/getting-started/installation/) to manage Python and its dependencies.

- Install `uv` and Python 3.12 or newer.
- Run `uv sync` to install the project's dependencies.

## Running the analyses

This project uses the Google Earth Engine (GEE) Python API, which requires a Google account registered for Earth Engine access. The first time you run the notebook, it will open a browser window asking you to sign in and authorize access; this only needs to happen once per machine.

Open and run `src/analyses/analyses.ipynb`.