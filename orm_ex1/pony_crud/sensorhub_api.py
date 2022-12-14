from fastapi import FastAPI
from pony.orm import db_session, set_sql_debug
from models import db, Channel, ChannelData, SensorHub
from fast_pony_crud import create_crud_routes
import uvicorn
import os
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


# ****************************** DB-helper function(s) ******************************************

@db_session
def hub_exists(name: str = None) -> bool:
    try:
        ch_query = Channel.select(lambda ch: ch.name == name)
        found = ch_query.first()
        #
        return found is not None
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")
        return False


@db_session
def channel_exists(name: str = None) -> bool:
    try:
        ch_query = Channel.select(lambda ch: ch.name == name)
        found = ch_query.first()
        #
        return found is not None
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")
        return False


@db_session
def add_channel(name: str = None, description: str = "", si_unit: str = "<unitless>") -> None:
    """ Create 'Channel'-instance in DB if not one already exist by same name """
    try:
        if channel_exists(name=name):
            print(f"Channel named '{name}' already exist - cannot create!")
        else:
            # Create channel:
            channel = Channel(name=name, description=description, si_unit=si_unit)
            # Write to DB:
            db.commit()
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")


@db_session
def add_hub(name: str = None, channels: set = None) -> None:
    """ Create 'SensorHub'-instance in DB if not one already exist by same name """
    try:
        sh_query = SensorHub.select(lambda ch: ch.name == name)
        found = sh_query.first()
        if found:
            print(f"SensorHub named '{name}' already exist - cannot create!")
        else:

            # Create channel:
            channel = SensorHub(name=name, description=description, si_unit=si_unit)
            # Write to DB:
            db.commit()
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")


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


def populate_db() -> None:
    """ Test function, just to add some 'Channel' and ' """
    # Just add some 'Channel'-instances in DB if they do not already exist:
    add_channel(name="bma280_temp", description="BMA280 temp reading", si_unit="Celcius")     # Not really a SI-unit but compatible (w. Kelvin) ...
    add_channel(name="sht721_hygro", description="SHT721 humidity reading", si_unit="%RH")   # Not really a SI-unit whatsoever, butbut ...
    add_channel(name="adxl355_accel", description="ADXL355 accel reading", si_unit="G") 
    #
    add_channel(name="bma280_temp", description="BMA280 temp reading", si_unit="Celcius")


# ****************************** Run API server ********************************

if __name__ == "__main__":
    # Add some dummy data first:
    populate_db()
    #
    create_crud_routes(db, app, prefix="/test_api", api_key="test123")
    #
    # Run API server - 'uvicorn' will automatically refresh API whenever code changes in folder!
    uvicorn.run(app, port=8889)

