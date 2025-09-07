# --- ECMWF forecast configuration ---

ECMWF_CONFIG = {
    "step": list(range(0, 168, 6)), #360
    "stream": "oper",
    "type": "fc",
    "levtype": "sfc",
    "model": "aifs-single",
    "param": ["tp","tcc","10u","10v","2t"],
    "target": "ecmwf_fc.grib2",
}

# --- MEPS forecast configuration ---

MEPS_CONFIG = {
    "url_ref_time" : "https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc?forecast_reference_time",
    # url = "https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc", 
    "url":"https://thredds.met.no/thredds/dodsC/metpplatest/met_forecast_1_0km_nordic_latest.nc?x,y,time,forecast_reference_time,latitude,longitude,air_temperature_2m,relative_humidity_2m,precipitation_amount,wind_direction_10m,wind_speed_10m,cloud_area_fraction"
}

ZARR = "ecmwf_forecast.zarr"

# --- Scheduler ---
UPDATE_INTERVAL_MINUTES = 10