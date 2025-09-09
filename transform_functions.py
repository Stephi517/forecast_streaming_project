#!/usr/bin/env python3

"""
Functions to transform model data and create wind quiver
"""

import xarray as xr
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import geoviews as gv
import holoviews as hv

def add_wind_components(ds, u_name=None, v_name=None, ws_name=None, wd_name=None):
    #adds wind speed and direction 
    if u_name and v_name:
        u = ds[u_name]
        v = ds[v_name]
        ds["ws"] = xr.ufuncs.sqrt(u**2 + v**2)
        # wd -> meteorological "coming from" 0° = North, 180° = South
        ds["wd"] = (xr.ufuncs.degrees(xr.ufuncs.arctan2(u, v)) + 180) % 360  
        ds["u"] = u
        ds["v"] = v
    # adds u and v component 
    elif ws_name and wd_name:
        ws = ds[ws_name]
        wd = ds[wd_name]
        ds["u"] = -ws * xr.ufuncs.sin(xr.ufuncs.radians(wd))   
        ds["v"] = -ws * xr.ufuncs.cos(xr.ufuncs.radians(wd))
        ds["ws"] = ws
        ds["wd"] = wd

    return ds


def transform_ECMWF(data):
    ds = data
    ds = data.rename({"tcc":"cloud",
                    "time":"forecast_reference_time"})
    ds = add_wind_components(ds, u_name="u10", v_name="v10")
    ds["t2m"] = ds["t2m"] - 273.15
    return ds 

def transform_MEPS(data):
    #ds = data[parameters]
    ds = data.rename({"precipitation_amount": "tp",
                    "wind_direction_10m": "wd",
                      "wind_speed_10m": "ws",
                      "cloud_area_fraction":"cloud",
                      "time":"valid_time",
                      "air_temperature_2m":"t2m"})
    ds = ds.assign(forecast_reference_time=data.forecast_reference_time,
                   t2m = ds["t2m"] - 273.15,
                   cloud = ds["cloud"] * 100)
    ds = add_wind_components(ds, ws_name="ws", wd_name="wd")
    ds = ds.assign_coords(step=((ds.valid_time - ds.forecast_reference_time)/3.6e+12).astype('float64'))
    ds = ds.swap_dims({'valid_time':'step'})
    return ds 

def make_wind_quiver(ds, step, stride=15):
    ds = ds.sel(step=step)

    w_speed = ds.ws.values[::stride, ::stride]
    wd_deg = ds.wd.values[::stride, ::stride]
    # Convert meteorological wind direction to "to-direction" for arrows and radiants for quiver
    wd_rad = xr.ufuncs.radians((270 - wd_deg) % 360) 

    lons = ds['longitude'].values
    lats = ds['latitude'].values

    if lons.ndim == 1 and lats.ndim == 1:
        # ECMWF data lat and lon are 1D coords
        lon, lat = np.meshgrid(lons[::stride], lats[::stride])
    else:
        # MEPS data lat lon (x,y) 2D
        lon = lons[::stride, ::stride]
        lat = lats[::stride, ::stride]

    data = np.column_stack([lon.ravel(), lat.ravel(), wd_rad.ravel(), w_speed.ravel()])
    
    vectors = hv.VectorField(data, kdims=['longitude', 'latitude'],
                            vdims=['wd_rad', 'w_speed']).opts(
                                magnitude='w_speed',
                                color="black",
                                scale=0.8,
                                #alpha=0.7,
                                #projection=ccrs.PlateCarree(),
                                #normalize=False,
                                # scale=1.5,
                                )
    return vectors

"""
def make_wind_quiver(ds, step, xcoord, ycoord, stride=20):
    u = ds["u"].sel(step=step).values
    v = ds["v"].sel(step=step).values
    ws = ds["ws"].sel(step=step).values
    wd = ds["wd"].sel(step=step).values
    lons = ds[xcoord].values
    lats = ds[ycoord].values

    # Handle lon/lat grid
    if lons.ndim == 1 and lats.ndim == 1:
        lons_sub = lons[::stride]
        lats_sub = lats[::stride]
        u_sub = u[::stride, ::stride]
        v_sub = v[::stride, ::stride]
        ws_sub = ws[::stride, ::stride]
        wd_sub = wd[::stride, ::stride]
        lon2d, lat2d = np.meshgrid(lons_sub, lats_sub)
    else:
        lons_sub = lons[::stride, ::stride]
        lats_sub = lats[::stride, ::stride]
        u_sub = u[::stride, ::stride]
        v_sub = v[::stride, ::stride]
        ws_sub = ws[::stride, ::stride]
        wd_sub = wd[::stride, ::stride]
        lon2d, lat2d = lons_sub, lats_sub

    # Flatten everything to 1D
    df = pd.DataFrame({
        "lon": lon2d.ravel(),
        "lat": lat2d.ravel(),
        "u": u_sub.ravel(),  
        "v": v_sub.ravel(),
        "ws": ws_sub.ravel(),
        "wd": wd_sub.ravel(),
    })

    vectors = gv.VectorField(
        df, kdims=["lon", "lat"], vdims=["u", "v"]
    ).opts(color="black",
        alpha=0.7,
        projection=ccrs.PlateCarree(),
        normalize=False,
        #magnitude="ws",
        scale=1.5,
    )
    return vectors
"""