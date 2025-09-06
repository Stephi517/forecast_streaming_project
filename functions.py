import xarray as xr
import numpy as np
import netCDF4
import pandas as pd
import cartopy.crs as ccrs
import geoviews as gv
import os

def check_for_new_global_forecast(client,config_args, last_dataset=None):
    """
    function to check for new forecast from ECMWF
    """
    filename = config_args.get("target", "ecmwf_fc.grib2")

    try:
        latest_fc = client.latest(
        **config_args)  # returns date of most recent matching forecast without downloading
    except Exception as e:
        print("Failed to get latest ECMWF forecast",e)    
        return last_dataset
    
    # If file exists, open and get current forecast time
    if os.path.exists(filename):
        last_dataset = xr.open_dataset(filename, engine="cfgrib", backend_kwargs={"indexpath": ""}, decode_timedelta=False)
        ref_last_forecast = last_dataset["time"].values
    else:
        ref_last_forecast = np.datetime64("1970-01-01")  # force a download

    if np.datetime64(latest_fc) > ref_last_forecast:
        print("New ECMWF forecast available, start download")
        last_dataset = client.retrieve(**config_args)
        last_dataset = xr.open_dataset(
            config_args["target"],
            engine="cfgrib",
            backend_kwargs={"indexpath": ""},
            decode_timedelta=False)
    else:
        print('No new ECMWF forecast file available')   
    
    return last_dataset    
  
def check_for_new_local_forecast(last_fc_time=None,previous_dataset=None):   
    #only fetch reference time
    url_ref_time = "https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc?forecast_reference_time"
    ncfile_ref_time   = netCDF4.Dataset(url_ref_time)
    ds = xr.open_dataset(xr.backends.NetCDF4DataStore(ncfile_ref_time))
    latest_fc_time = ds.forecast_reference_time.values    

    if latest_fc_time > np.datetime64(last_fc_time) or last_fc_time is None:
        # fetch full dataset
        # url = "https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc"   
        url = "https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc?x,y,time,forecast_reference_time,latitude,longitude,air_temperature_2m,relative_humidity_2m,precipitation_amount,wind_direction_10m,wind_speed_10m,cloud_area_fraction"
        ncfile   = netCDF4.Dataset(url)
        dataset = xr.open_dataset(xr.backends.NetCDF4DataStore(ncfile)) 
        return dataset, latest_fc_time
    else:
        print("No new MEPS forecast available, keeping previous data")
        return previous_dataset, last_fc_time    

def add_wind_components(ds, u_name=None, v_name=None, ws_name=None, wd_name=None):
    #adds wind speed and direction 
    if u_name and v_name:
        u = ds[u_name]
        v = ds[v_name]
        ds["ws"] = np.sqrt(u**2 + v**2)
        ds["wd"] = (np.degrees(np.arctan2(u, v)) + 360) % 360  
        ds["u"] = u
        ds["v"] = v
    # adds u and v component 
    elif ws_name and wd_name:
        ws = ds[ws_name]
        wd = np.deg2rad(ds[wd_name])
        ds["u"] = -ws * np.sin(wd)   
        ds["v"] = -ws * np.cos(wd)
        ds["ws"] = ws
        ds["wd"] = ds[wd_name]

    return ds


def transform_ECMWF(data):
    ds = data
    ds = data.rename({"tcc":"cloud",
                    "time":"forecast_reference_time"})
    ds = add_wind_components(ds, u_name="u10", v_name="v10")
    return ds 

def transform_MEPS(data):
    ds = data.assign_coords(forecast_reference_time=data.forecast_reference_time)
    #ds = data[parameters]
    ds = ds.rename({"precipitation_amount": "tp",
                    "wind_direction_10m": "wd",
                      "wind_speed_10m": "ws",
                      "cloud_area_fraction":"cloud",
                      "time":"valid_time",
                      "air_temperature_2m":"t2m"})
    ds['t2m'] = ds.t2m - 273.15
    ds['cloud'] = ds['cloud'] * 100
    ds = add_wind_components(ds, ws_name="ws", wd_name="wd")
    ds = ds.assign_coords(step=((ds.valid_time - ds.forecast_reference_time)/3.6e+12).astype('float64'))
    ds = ds.swap_dims({'valid_time':'step'})
    # forecast_reference_time=np.datetime64(int(ds.attrs['meps_forecast_reference_time']), 's').astype('datetime64[ns]'),
    return ds 

def make_wind_quiver(ds, step, xcoord, ycoord, stride=20):
    # Select step
    u = ds["u"].sel(step=step).values
    v = ds["v"].sel(step=step).values
    ws = ds["ws"].sel(step=step).values
    wd = ds["wd"].sel(step=step).values
    lons = ds[xcoord].values
    lats = ds[ycoord].values

    # Handle lon/lat grid
    if lons.ndim == 1 and lats.ndim == 1:
        # 1D coordinate vectors
        lons_sub = lons[::stride]
        lats_sub = lats[::stride]
        u_sub = u[::stride, ::stride]
        v_sub = v[::stride, ::stride]
        ws_sub = ws[::stride, ::stride]
        wd_sub = wd[::stride, ::stride]
        lon2d, lat2d = np.meshgrid(lons_sub, lats_sub)
    else:
        # 2D coordinate grid
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

    # GeoViews VectorField
    vectors = gv.VectorField(
        df, kdims=["lon", "lat"], vdims=["u", "v"]
    ).opts(color="black",
        alpha=0.7,
        projection=ccrs.PlateCarree(),
        normalize=False,
        #magnitude="ws",
        scale=0.1,
    )
    return vectors
