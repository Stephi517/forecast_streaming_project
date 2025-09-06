import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from ecmwf.opendata import Client
import panel as pn
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import FIXED_SIZING_MODE
silence(FIXED_SIZING_MODE)

import time
from functions import *
from vizualize_forecasts import build_forecast_dashboard
from data_store import ForecastStore

client = Client("ecmwf", beta=False)
filename = "ecmwf_fc.grib2"

config_args = {
    "step": list(range(0, 360, 6)),
    "stream": "oper",
    "type": "fc",
    "levtype": "sfc",
    "model": "aifs-single",
    "param": ["tp","tcc","10u","10v"],
    "target": filename,
}
time1 = time.time()
store = ForecastStore()
global_data = None
regional_data = None
last_meps_time = None 

def update_models():
    global global_data, regional_data, last_meps_time
    print("Updating forecasts at", datetime.datetime.now())

    try:
        global_data = check_for_new_global_forecast(client, config_args, global_data)
        if global_data is not None:
            global_data = transform_ECMWF(global_data)
            store.update(ecmwf=global_data)
    
    except Exception as e:
        print("ECMWF update failed:", e)
        
    try:
        regional_data, last_meps_time = check_for_new_local_forecast(last_fc_time=last_meps_time,previous_dataset=regional_data)
        
        if regional_data is not None:
            # Only transform if dataset has required variables
            required_vars = ["time", "latitude","longitude"]
            if all(var in regional_data.variables or var in regional_data.coords for var in required_vars):
                regional_data = transform_MEPS(regional_data)
                store.update(meps=regional_data)
                print("MEPS update successful")
            else:
                print("MEPS dataset not ready yet, skipping update")
        else:
            print("No new MEPS forecast, keeping previous data")

    except Exception as e:
        print("MEPS update failed:", e)

# Initial load
update_models()

# --- Build dashboard ---
models = {}
if store.models.get("ECMWF") is not None:
    models["ECMWF"] = store.models["ECMWF"]
if store.models.get("MEPS") is not None:
    models["MEPS"] = store.models["MEPS"]

dashboard = build_forecast_dashboard(models, dashboard_title="Forecast")

time2 = time.time()
print(time2-time1)
dashboard.show()

# --- Scheduler to update every 30 min ---
scheduler = BackgroundScheduler()
scheduler.add_job(update_models, "interval", minutes=30)
scheduler.start()