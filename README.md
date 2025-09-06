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
create virtual environment
```bash
pip install -r requirements.txt

python data_pipeline.py
```
