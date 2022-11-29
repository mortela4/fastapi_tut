"""
DB model of cyper-physical system w. sensors(IN-values) and actuators(OUT-values), where IN/OUT-channels are represented by 'Channel'-objects.
"""

from pony.orm import Database, PrimaryKey, Required, Optional, Set, db_session, set_sql_debug, FloatArray
import time
import random

SQL_DEBUG = False

db = Database()
db.bind('sqlite', ':memory:')   # In-memory SQLite DB only --> for testing ...

# Enable SQL debug:
if SQL_DEBUG:
    set_sql_debug()

# Model:

class Channel(db.Entity):
    name = PrimaryKey(str)
    is_output = Optional(bool, default=False)
    description = Optional(str, default="<sensor IN-type>" if is_output else "<actuator OUT-type>")
    si_unit = Optional(str, default="<unitless>")
    scale_factor = Optional(float, default=1.0)
    # sample_freq = Optional(float, default=1.0)    --> Hz
    # num_bits = Optional(int, default=16)          --> TODO: relevant???
    ch_data_sources = Set("ChannelData")

class ChannelData(db.Entity):
    ch_id = PrimaryKey(int, auto=True)
    time_points = Optional(FloatArray)
    data_points = Optional(FloatArray)
    from_channel = Required(Channel)
    to_hub = Optional("SensorHub")

class SensorHub(db.Entity):
    ser_no = PrimaryKey(int)
    name = Required(str)
    channels = Set(ChannelData)
    

# Create database tables:
db.generate_mapping(create_tables=True)


# Create sensor entities:
@db_session
def create_channels_and_hubs():
    bma380_temp = Channel(name="BMA280_temp", si_unit="Celcius")
    adxl255_accel = Channel(name="ADXL255_accel")
    fxs3008_pressure = Channel(name="FXS3008_pressure", si_unit="Bar")
    # Then sensor-hub entities ...
    SensorHub(ser_no=123, name="TestHub1", channels=(ChannelData(from_channel=bma380_temp)))
    SensorHub(ser_no=223, name="TestHub2", channels=(ChannelData(from_channel=bma380_temp), ChannelData(from_channel=adxl255_accel)))
    SensorHub(ser_no=323, name="TestHub3", channels=(ChannelData(from_channel=bma380_temp), ChannelData(from_channel=fxs3008_pressure)))
    SensorHub(ser_no=533, name="TestHub4", channels=(ChannelData(from_channel=bma380_temp)))


# Retrieve from DB:
@db_session
def get_entities_and_show_fields():
    peticular_hub = SensorHub[123]                              # Retrieve single entity
    print(f"Name of hub w. serial no.123: {peticular_hub.name}\n")
    #
    hubs = SensorHub.select(lambda hub: hub.ser_no > 200)       # Retrieve multiple entitities
    print("All hubs with serial no. over 200:")
    for hub in hubs:
        print(f"{hub.name}")
        print(f"SerNo = {hub.ser_no}")
        if 0 == len(hub.channels):
            print("No channels??")
        else:
            print("Channels:")
            for ch in hub.channels:
                print(f"\t{ch.from_channel.name}")

"""
@db_session
def add_data_to_hub(id: int = -1, tsd: list = None) -> None:
    hub = None
    if id < 0:
        print("Invalid ID given! Cannot proceed ...")
        return
    if tsd is None:
        print("No data given! Cannot proceed ...")
        return
    # Get hub:
    try:
        hub = SensorHub[id]   
        if hub is None:
           print(f"No 'SensorHub' entity w. ID {id} found!! Giving up ...")
           return                            
    except Exception as ex:
        print(f"Query for 'SensorHub' entity w. ID {id} exploded!! Reason: {ex}")
        return
    #
    for ts_point in tsd:
        time_point, data_point = ts_point
        #
        hub.time_points.append(time_point) 
        hub.data_points.append(data_point)
    #
    print(f"Added {len(tsd)} data-points to hub entity ...")

@db_session
def show_data_from_hub(id: int = -1) -> None:
    hub = None
    if id < 0:
        print("Invalid ID given! Cannot proceed ...")       # Redundant - will be caught by exception-check below anyway, but OK here ...
        return
    # Get hub:
    try:
        hub = SensorHub[id]    
        if hub is None:
            print(f"No 'SensorHub' entity w. ID {id} found!! ID={id} non-existent!")            
            return          
    except Exception as ex:
        print(f"Query for 'SensorHub' entity w. ID {id} exploded!! Resaon: {ex}")
        return
    #
    x_vals = hub.time_points
    y_vals = hub.data_points
    #
    num_samples = len(x_vals)
    for idx in range(num_samples):
        print(f"Sample {idx}: time = {x_vals[idx]}, value = {y_vals[idx]}")
"""

# Test-helpers:

def generate_dummy_data(num_samples: int = 10, min_val: int = -100, max_val: int = 100, factor: float = 0.025) -> list:
    start_time = time.time()
    time_points = list()
    data_points = list()
    #
    for _ in range(num_samples):
        time_point = time.time() - start_time
        time_points.append(time_point)
        #
        data_point = random.randint(min_val, max_val) * factor
        data_points.append(data_point)
        #
        time.sleep(0.1)
    #
    time_series_data = list(zip(time_points, data_points))
    #
    return time_series_data


# ***************************** FUNCTIONAL TEST ******************************************

if __name__ == "__main__":
    create_channels_and_hubs()
    get_entities_and_show_fields()
    # ts_data = generate_dummy_data()
    # add_data_to_hub(id=533, tsd=ts_data)
    # show_data_from_hub(id=533)

    # Finalize
    db.disconnect()











