import panel as pn
import holoviews as hv
import hvplot.xarray
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import time 

from transform_functions import make_wind_quiver

pn.extension()
hv.extension("bokeh")

def build_forecast_dashboard(models: dict, dashboard_title="Weather Forecast"):
    def make_plots_for_step(ds, step, stride, variables_to_plot):
        xcoord = "longitude" if "longitude" in ds.coords else "lon"
        ycoord = "latitude" if "latitude" in ds.coords else "lat"

        def _plot(var, title, cmap, clabel):
            if (xcoord in ds.coords) and (ycoord in ds.coords):
                return ds[var].sel(step=step).hvplot.quadmesh(
                    x=xcoord,
                    y=ycoord,
                    geo=True,
                    coastline="110m",
                    rasterize=True,
                    project=True,
                    projection=ccrs.PlateCarree(),
                    title=title,
                    cmap=cmap,
                    clabel=clabel,
                )
            else:
                ds_latlon = ds.assign_coords(
                    lon=(("y", "x"), ds["longitude"].values),
                    lat=(("y", "x"), ds["latitude"].values),
                )
                return ds_latlon[var].sel(step=step).hvplot.quadmesh(
                    x="lon",
                    y="lat",
                    geo=True,
                    coastline="110m",
                    rasterize=True,
                    project=True,
                    projection=ccrs.PlateCarree(),
                    title=title,
                    cmap=cmap,
                    clabel=clabel,
                )

        plots_list = []
        if "cloud" in variables_to_plot:
            plots_list.append(_plot("cloud", "Total cloud cover", "Blues", "%"))
        if "tp" in variables_to_plot:
            plots_list.append(_plot("tp", "Total precipitation", "Blues", "kg/m²"))
        if "wind" in variables_to_plot:
            wind_speed_bg = _plot("ws", "Wind speed (10m)", "YlGnBu", "m/s")
            wind_quiver = make_wind_quiver(ds, step, xcoord, ycoord, stride=stride)
            plots_list.append(wind_speed_bg * wind_quiver)
        if "wind_direction" in variables_to_plot:
            wind_dir = _plot("wd", "Wind direction (10m)", "twilight", "°")
            plots_list.append(wind_dir)
        if "temperature" in variables_to_plot:
            plots_list.append(_plot("t2m", "2m Temperature", "coolwarm", "°C"))

        return hv.Layout(plots_list).cols(2)

    tabs = pn.Tabs()
    for name, ds in models.items():
        # Skip dataset that only checks the reference time
        if ds is None or not hasattr(ds, "step"):
            continue

        steps = ds.step.values
        step_widget = pn.widgets.DiscreteSlider(
            name="Forecast hour [h]",
            options=list(steps),
            value=steps[0],
        )

        if name=="ECMWF":
            variables = ["cloud","tp","wind","temperature"]
            stride = 30  
        else: 
            variables = ["cloud","tp","wind","temperature"]
            stride = 60

        @pn.depends(step_widget)
        def model_panel(step, ds=ds, name=name, stride=stride, variables=variables):  
            forecast_reference_time = pd.to_datetime(ds.forecast_reference_time.values).strftime("%Y-%m-%d %H:%M UTC")
            forecast_valid_time = pd.to_datetime(ds.valid_time.sel(step=step).values).strftime("%Y-%m-%d %H:%M UTC")

            title_pane = pn.pane.Markdown(f"## {name} Forecast valid time: {forecast_valid_time}", align="center")
            subtitle_pane = pn.pane.Markdown(f"Forecast reference time: {forecast_reference_time}", align="start")
            plots = make_plots_for_step(ds, step, stride=stride, variables_to_plot=variables)

            # model info pane
            if name == "ECMWF":
                model_info = """
                ### Model Information: ECMWF Artificial Intelligence Forecasting System (AIFS) deterministic model  
                - Horizontal resolution: 0.25° x 0.25° lat/lon grid
                - Forecast range: 15 days  
                - Update frequency: 2 forecast runs per day (00/12 UTC)
                """
            elif name == "MEPS":
                model_info = """
                ### Model Information: MEPS  
                - Based on model data from MEPS (MetCoOp-Ensemble Prediction System) and observations
                - Source: Based on data from MET Norway, https://thredds.met.no/thredds/catalog/metpplatest/catalog.html
                - Horizontal resolution: 2.5 km  
                - Forecast range: 66 hours  
                - Update frequency: every 3 hours   
                """
            else:
                model_info = "### Model Information not available."

            info_pane = pn.pane.Markdown(model_info, align="start")

            return pn.Column(title_pane, subtitle_pane, plots, info_pane) 

        tabs.append((name, pn.Column(step_widget, model_panel)))

    template = pn.template.FastListTemplate(
        title=dashboard_title,
        main=[tabs],
    )
    return template
