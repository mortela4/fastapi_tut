from fast_pony_crud import create_crud_routes
import uvicorn
import os

from fastapi import FastAPI
from pony.orm import db_session, set_sql_debug

from models import db, Channel, ChannelData, SensorHub
from db_actions import get_channel_by_name, get_hub_by_name, get_hub_by_serno, get_hub_data, channel_exists, add_channel, add_hub, add_sensor_data

# For functional test:
import time
import random


USE_PERSISTENT_DATA = False                 # If false, DB in RAM is started over again on each run.
#
if USE_PERSISTENT_DATA:
    SQLITE_FILE = "sensorhub_db.sqlite"
else:
    SQLITE_FILE = ":sharedmemory:"    # Use this for basic testing of logic etc. (Required when using w. FastAPI/PonyCRUD)

USE_API_KEY = True
#
if USE_API_KEY:
    API_TEST_KEY = "test123"
else:
    API_TEST_KEY = None


# FastAPI app object:
app = FastAPI()

# DB connection:
database_url = os.environ.get('DATABASE_URL')      # If NOT set (i.e. 'None' returned), use SQLite file as DB. Else, must be valid PostgresDB URL.
if database_url:
    db.bind(provider='postgres', dsn=database_url)
else: 
    db.bind(provider='sqlite', filename=SQLITE_FILE, create_db=True)

# Map model-classes to tables, and - create tables in DB:
db.generate_mapping(create_tables=True)



# ******************************** Test-functions ***********************************

def generate_dummy_sensor_data(num_samples: int = 10, min_val: int = -100, max_val: int = 100, factor: float = 0.025) -> list:
    #
    values = list()
    #
    for _ in range(num_samples):
        time_point = time.time()
        data_point = random.randint(min_val, max_val) * factor
        values.append( (time_point, data_point) )
    #
    return values

def plot_data(ch_name: str = None, data: list = None) -> None:
    pass


def populate_db() -> None:
    """ Test function, just to add some 'Channel' and ' """
    # Just add some 'Channel'-instances in DB if they do not already exist:
    add_channel(name="bma280_temp", description="BMA280 temp reading", si_unit="Celcius")     # Not really a SI-unit but compatible (w. Kelvin) ...
    add_channel(name="sht721_hygro", description="SHT721 humidity reading", si_unit="%RH")   # Not really a SI-unit whatsoever, butbut ...
    add_channel(name="adxl355_accel", description="ADXL355 accel reading", si_unit="G") 
    # Make this FAIL:
    add_channel(name="bma280_temp", description="BMA280 temp reading", si_unit="Celcius")
    #
    # Then, add some 'SensorHub' instances:
    add_hub(hub_name="Hubby1", ser_no=123)
    add_hub(hub_name="Hubble", ser_no=456)
    add_hub(hub_name="HubHub", ser_no=789)
    # Make this FAIL:
    add_hub(hub_name="Hubby2", ser_no=456)      # Triggers exception!
    add_hub(hub_name="Hubble", ser_no=1000)
    #
    # Finally, with hubs and channels in place, we can connect DATA to hubs w. channel specified:
    dummy_data = generate_dummy_sensor_data(min_val=-5, max_val=10, factor=0.95)
    add_sensor_data(ser_no=123, channel_name="bma280_temp", sensor_data=dummy_data)
    #
    dummy_data = generate_dummy_sensor_data(min_val=30, max_val=50, factor=0.95)
    add_sensor_data(ser_no=123, channel_name="sht721_hygro", sensor_data=dummy_data)
    # Make this FAIL:
    dummy_data = generate_dummy_sensor_data(min_val=0, max_val=100, factor=0.01)
    add_sensor_data(ser_no=123, channel_name="adxl343_accel", sensor_data=dummy_data)


def show_data(hub_id: int = None, verbose: bool = True) -> None:
    dd = get_hub_data(hub_id=hub_id)
    #
    for k, v in dd.items():
        print(f"\nData from hub {hub_id}:")
        print("==========================")
        if verbose:
            print(f"Values from channel {k}:\n{v}\n")
        plot_data(ch_name=k, data=v)


# ****************************** Populate DB with some (dummy-)data and run API server ********************************

if __name__ == "__main__":
    # Add some dummy data first:
    populate_db()
    # Then, check channel-data for some hub(s):
    show_data(hub_id=123)
    # Let 'FastPonyCRUD' library AUTOMAGICALLY create GET/PUT/POST/DELETE-endpoints for each entity-model!
    create_crud_routes(db, app, prefix="/test_api", api_key="test123")
    #
    # Run API server - 'uvicorn' will automatically refresh API whenever code changes in folder!
    uvicorn.run(app, port=8889)

