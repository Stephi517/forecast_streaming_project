from ecmwf.opendata import Client
import panel as pn
import time
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import FIXED_SIZING_MODE
silence(FIXED_SIZING_MODE)

from transform_functions import *
from update_functions import *
from visualization import build_forecast_dashboard
from data_store import ForecastStore
from config import ECMWF_CONFIG, MEPS_CONFIG, UPDATE_INTERVAL_MINUTES, ZARR

client = Client("ecmwf", beta=False)

store = ForecastStore()
global_data = None
regional_data = None
last_meps_time = None 

def update_models():
    global global_data, regional_data, last_meps_time
    print(f"Updating forecasts at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    try:
        global_data = check_for_new_global_forecast(client, ECMWF_CONFIG, ZARR, global_data)
        if global_data is not None:
            global_data = transform_ECMWF(global_data)
            store.update(ecmwf=global_data)
    
    except Exception as e:
        print("ECMWF update failed:", e)
        
    try:
        regional_data, last_meps_time = check_for_new_local_forecast(MEPS_CONFIG,last_fc_time=last_meps_time,previous_dataset=regional_data)
          
        # Only transform if dataset has required variables
        required_vars = ["time", "latitude","longitude"]
        if regional_data is not None and all(var in regional_data.variables or var in regional_data.coords for var in required_vars):
            regional_data = transform_MEPS(regional_data)
            # Persist in memory to make plotting faster
            #regional_data = regional_data.persist()
            store.update(meps=regional_data)
    except Exception as e:
        print("MEPS update failed:", e)
    print("Models updated")    

       
start_time = time.time()
update_models()
# --- Build dashboard ---
models = {}
if store.models.get("ECMWF") is not None:
    models["ECMWF"] = store.models["ECMWF"]
if store.models.get("MEPS") is not None:
    models["MEPS"] = store.models["MEPS"]

dashboard = build_forecast_dashboard(models, dashboard_title="Forecast")

print(f"Dashboard built. Total load time: {time.time() - start_time:.1f} seconds")

dashboard.servable()
#dashboard.show()

# --- Periodic update every x minutes using Panel ---
def periodic_update():
    update_models()

pn.state.add_periodic_callback(periodic_update, UPDATE_INTERVAL_MINUTES * 60 * 1000)

