# visualize_last_forecast

This project provides a prototype of an interactive dashboard for visualizing **ECMWF** and **MEPS** weather forecasts.  
It downloads the latest model runs, processes them and provides maps of cloud cover, precipitation, wind, and temperature in your browser.

It uses:
- [Panel](https://panel.holoviz.org/) & [Holoviews](https://holoviews.org/) → interactive visualization
- [xarray](https://xarray.pydata.org/) → dataset handling

Weather forecasts are fetched from:  
- [ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata) → global forecast
- [MET Norway Thredds](https://thredds.met.no/thredds/catalog/metpplatest/catalog.html) → regional forecasts (MEPS)

---
## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Stephi517/forecast_streaming_project.git
```
### 2. Create a virtual environment

On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install requirements 
```bash
pip install -r requirements.txt
```
### 4. Run data_pipeline.py
run:
```bash
python -m panel serve forecast_stream.py --show  
```
in environment and keep terminal open to have the plots automatically updated

---
## Project structure

config.py -> provides the specifications of the ECMWF and MEPS download and the intervall times for update check-up

data_store.py -> stores model forecast

forecast_stream.py -> main file

transform_functions.py -> contains functions that transform and modify the datasets

update_functions.py -> contains functions that are to check for updated forecasts

visualization.py -> builds the visualization dashboard
