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


# ****************************** DB-helper function(s) (must have '@db_session' decorator) ******************************************

@db_session
def get_channel_by_name(ch_name: str = None, verbose: bool = False) -> Channel:
    try:
        ch_query = Channel.select(lambda ch: ch.name == ch_name)
        #
        if verbose:
            if 1 < ch_query.count():
                print(f"WARNING: duplicate entities of 'Channel' object found!")
            elif 1 == ch_query.count():
                print(f"INFO: found one entity of 'Channel' object, named '{ch_name}'")
            else:
                print(f"INFO: found NO entity of 'Channel' object, named '{ch_name}'")
        #
        return ch_query.first()
    except Exception as ex:
        # NOTE: returning 'None' is probably correct here!
        print(f"Database operation exploded! Reason: {ex}")
        return None


@db_session
def get_hub_by_serno(ser_no: int = None) -> Channel:
    try:
        sh_query = SensorHub.select(lambda sh: sh.ser_no == ser_no)
        return sh_query.first()
    except Exception as ex:
        # NOTE: returning 'None' is probably correct here!
        print(f"Database operation exploded! Reason: {ex}")
        return None


@db_session
def get_hub_by_name(hub_name: str = None) -> Channel:
    try:
        sh_query = SensorHub.select(lambda sh: sh.name == hub_name)
        return sh_query.first()
    except Exception as ex:
        # NOTE: returning 'None' is probably correct here!
        print(f"Database operation exploded! Reason: {ex}")
        return None


@db_session
def hub_exists(ser_no: int = None, name: str = None) -> bool:
    """ Use this function to ensure BOTH hub serial no AND name are both unique """
    found = None 
    try:
        # First check - on primary key:
        if ser_no is not None:
            found = get_hub_by_serno(ser_no=ser_no)
        # Second check - on required field:
        if name is not None:
            found = get_hub_by_name(hub_name=name)
        #
        return found is not None
    except Exception as ex:
        # NOTE: just an example - NOT proper handling! (should re-throw and let upper layer handle it ...)
        print(f"Database operation exploded! Reason: {ex}")
        return False


@db_session
def channel_exists(name: str = None) -> bool:
    try:
        found = get_channel_by_name(ch_name=name)
        return found is not None
    except Exception as ex:
        # NOTE: just an example - NOT proper handling! (should re-throw and let upper layer handle it ...)
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
            Channel(name=name, description=description, si_unit=si_unit)
            # Write to DB:
            db.commit()
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")


@db_session
def add_hub(hub_name: str = None, ser_no: int = None, channel_names: list = None) -> None:
    """ Create 'SensorHub'-instance in DB if not one already exist by same name """
    if ser_no is None or hub_name is None:
        print("ERROR: both serial number and hub-name MUST be specified!!")
        return
    try:
        if hub_exists(ser_no=ser_no, name=hub_name):
            print(f"SensorHub named '{hub_name}' already exist - cannot create!")
        else:
            # Create channel:
            SensorHub(ser_no=ser_no, name=hub_name)
            # Write to DB:
            db.commit()
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")


@db_session
def add_sensor_data(ser_no: int = None, channel_name: str = None, sensor_data: list = None) -> None:
    """ Create 'ChannelData'-instance(s) in DB """
    hub = None 
    channel = None
    try:
        # Hub must exist:
        if not hub_exists(ser_no=ser_no):
            print(f"SensorHub with serial no = {ser_no} does NOT exist - cannot map data!")
            return  # Function makes no change in DB ...
        else:
            hub = SensorHub[ser_no]
        # Specified channel must exist:
        if not channel_exists(name=channel_name):
            print(f"Channel named '{channel_name}' does NOT exist - cannot map data!")
            return  # Function makes no change in DB ...
        else:
            channel = get_channel_by_name(ch_name=channel_name)
        # Create data:
        for sdata in sensor_data:
            tval, dval = sdata
            # Create ChannelData entity:
            ChannelData(time_point=tval, data_point=dval, from_channel=channel, to_hub=hub)
        # Write to DB:
        db.commit()
    except Exception as ex:
        print(f"Database operation exploded! Reason: {ex}")


@db_session
def get_hub_data(hub_id: int = None, verbose: bool = False) -> dict:
    data_dict = dict()
    channel_datas = ChannelData.select(lambda cd: cd.to_hub.ser_no == hub_id)
    if channel_datas:
        for ch_data in channel_datas:
            ch_name = ch_data.from_channel.name
            #
            tv = ch_data.time_point
            dv = ch_data.data_point
            #
            if ch_name in data_dict.keys():
                data_dict[ch_name].append( (tv, dv))
            else:
                data = [ (tv, dv) ]
                data_dict[ch_name] = data
            if verbose:
                print(f"Data {ch_data.data_id}: time={tv}, value={dv}, from channel: '{ch_data.from_channel.name}'")
            
    #
    return data_dict


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
        if verbose:
            print(f"Values from channel {k}:\n{v}\n")
        plot_data(ch_name=k, data=v)


# ****************************** Populate DB with some (dummy-)data and run API server ********************************

if __name__ == "__main__":
    # Add some dummy data first:
    populate_db()
    # Then, check channel-data for some hub(s):
    show_data(hub_id=123)
    #
    create_crud_routes(db, app, prefix="/test_api", api_key="test123")
    #
    # Run API server - 'uvicorn' will automatically refresh API whenever code changes in folder!
    uvicorn.run(app, port=8889)

