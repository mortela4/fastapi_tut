"""
DB model of cyper-physical system w. sensors(IN-values) and actuators(OUT-values)
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

class Sensor(db.Entity):
    partno = Required(str)
    bus_type = Required(str)    # one of "I2C", "SPI" or "UART"
    unit_name = Optional(str)
    hubs_where_used = Set("SensorHub")

class SensorHub(db.Entity):
    ser_no = PrimaryKey(int)
    name = Required(str)
    bus_ids = Optional(str, default="<none>")   # Comma-separated list of bus-connection strings, i.e. 'SPI_0.3' means ChipSelect no.3 on SPI-controller no.0
    sensors = Set(Sensor)
    time_points = Optional(FloatArray)
    data_points = Optional(FloatArray)

# Create database tables:
db.generate_mapping(create_tables=True)


# Create sensor entities:
@db_session
def create_entities():
    bma380 = Sensor(partno="BMA280", bus_type="SPI", unit_name="RhT")
    adxl255 = Sensor(partno="ADXL255", bus_type="UART", unit_name="G")
    fxs3008 = Sensor(partno="FXS3008", bus_type="I2C", unit_name="Bar")
    # Then sensor-hub entities ...
    SensorHub(ser_no=123, name="TestHub1", bus_ids="SPI_0.3,UART0,I2C1.0x48", sensors=(bma380, adxl255, fxs3008))
    SensorHub(ser_no=223, name="TestHub2", bus_ids="SPI_0.1,UART3,I2C1.0x56", sensors=(adxl255, fxs3008))
    SensorHub(ser_no=323, name="TestHub3", bus_ids="SPI_3.0,I2C1.0x71", sensors=(bma380, fxs3008))
    SensorHub(ser_no=533, name="TestHub4")

create_entities()
db.commit()     # Redundant, done at exit from 'create_etities()' func)

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
        print(f"bus-ID(s) = {hub.bus_ids}")
        if 0 == len(hub.sensors):
            print("No sensors connected ...")
        else:
            print("Sensors connected:")
            for sensor in hub.sensors:
                print(f"\t{sensor.partno}")


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
    """ Shows ALL time-series data from 'SensorHub' entity with ID='id' """
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
    get_entities_and_show_fields()
    ts_data = generate_dummy_data()
    add_data_to_hub(id=533, tsd=ts_data)
    show_data_from_hub(id=533)

    # Finalize
    db.disconnect()











