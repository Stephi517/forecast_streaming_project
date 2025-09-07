#!/usr/bin/env python3

"""
Functions to check & update forecasts
"""

import xarray as xr
import numpy as np
import netCDF4
import os


def merge_ECMWF_grib(grib_file):
    ds_main = xr.open_dataset(grib_file,
            engine="cfgrib",
            backend_kwargs={"indexpath": ""},
            decode_timedelta=False,
            filter_by_keys={"shortName": ["tp","tcc","10u","10v"]})
    ds_t = xr.open_dataset(grib_file, engine="cfgrib",
                           backend_kwargs={"indexpath": ""},
                           decode_timedelta=False,
                           filter_by_keys={"shortName": "2t"})
    ds_t = ds_t.assign_coords(step=((ds_t.valid_time - ds_t.time) / np.timedelta64(1, "h")).astype("float64")).drop(["heightAboveGround"])
    return xr.merge([ds_main, ds_t], compat="override")

def check_for_new_global_forecast(client, config_args, zarr_file , last_dataset=None):
    """
    function to check for new forecast from ECMWF
    """
    try:
        latest_fc = client.latest(
        **config_args)  # returns date of most recent matching forecast without downloading
    except Exception as e:
        print("Failed to get latest ECMWF forecast",e)    
        return last_dataset
    
    # If Zarr file exists, open it and get current forecast reference time
    if os.path.exists(zarr_file):
        last_dataset = xr.open_zarr(zarr_file, decode_timedelta=False)
        ref_last_forecast = last_dataset["time"].values
    else:
        ref_last_forecast = np.datetime64("1970-01-01")  # force download    

      # Compare times
    if np.datetime64(latest_fc) > ref_last_forecast:
        print("New ECMWF forecast available")
        client.retrieve(**config_args)
        # Merge datasets from GRIB
        new_dataset = merge_ECMWF_grib(config_args["target"])
        # Save merged dataset to Zarr, specify version to silence future warning 
        new_dataset.to_zarr(zarr_file, mode="w", zarr_format=2)

        return new_dataset
    else:
        print("No new ECMWF forecast available")
        return last_dataset   
  
def check_for_new_local_forecast(config_args,last_fc_time=None,previous_dataset=None):
    #only fetch reference time
    url_ref_time = config_args["url_ref_time"]
    ncfile_ref_time   = netCDF4.Dataset(url_ref_time)
    ds = xr.open_dataset(xr.backends.NetCDF4DataStore(ncfile_ref_time))
    latest_fc_time = ds.forecast_reference_time.values    
    if latest_fc_time > np.datetime64(last_fc_time) or last_fc_time is None:
        # fetch full dataset  
        url = config_args["url"]
        ncfile   = netCDF4.Dataset(url)
        dataset = xr.open_dataset(xr.backends.NetCDF4DataStore(ncfile),chunks={"time": 1, "x": 500, "y": 500}) 
        print("Updated MEPS")
        return dataset, latest_fc_time
    else:
        print("No new MEPS forecast available, keeping previous data")
        return previous_dataset, last_fc_time   