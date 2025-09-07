# visualize_last_forecast

This project provides an interactive dashboard for visualizing **ECMWF** and **MEPS** weather forecasts.  
It downloads the latest model runs, processes them into a consistent format, and renders maps of cloud cover, precipitation, wind, and temperature in your browser.

Built with:
- [Panel](https://panel.holoviz.org/) & [Holoviews](https://holoviews.org/) → interactive visualization
- [xarray](https://xarray.pydata.org/) → dataset handling
- [ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata) → global forecast access
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
run either:
```bash
python data_pipeline.py
```
or 
```bash
panel serve data_pipeline.py --autoreload --show
```
in environment and keep Terminal open to have the plots automatically updated

python -m panel serve data_pipeline.py --show
Don’t use --autoreload in production; only when you’re editing code.

Then your scheduler will run exactly every 30 min.
