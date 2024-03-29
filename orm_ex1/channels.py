"""
@file channels.py

DB model of cyper-physical system w. sensors(IN-values) and actuators(OUT-values), where IN/OUT-channels are represented by 'Channel'-objects.

Stand-alone application; provides
- models
- DB binding and creation
- creation of model instances, and WRITE of them to DB
- READ of data from DB, w. demo of selection based on one or multiple keys
- presentation (plotting) of data
"""

from pony.orm import Database, PrimaryKey, Required, Optional, Set, db_session, set_sql_debug, FloatArray
import time
from datetime import datetime
import random
from dataclasses import dataclass, asdict, field
# If plotting data is required:
import matplotlib.pyplot as plt


SQL_DEBUG = False

db = Database()
db.bind('sqlite', ':memory:')   # In-memory SQLite DB only --> for testing ...

# Enable SQL debug:
if SQL_DEBUG:
    set_sql_debug()

# Models:

class Channel(db.Entity):
    name = PrimaryKey(str)
    is_output = Optional(bool, default=False)
    description = Optional(str, default="<sensor IN-type>" if is_output else "<actuator OUT-type>")
    si_unit = Optional(str, default="<unitless>")
    scale_factor = Optional(float, default=1.0)
    sample_freq = Optional(float, default=1.0)    # --> Hz
    num_bits = Optional(int, default=16)          # --> TODO: relevant???
    ch_data_sources = Set("ChannelData")

class ChannelData(db.Entity):
    ch_id = PrimaryKey(int, auto=True)
    start_time = Optional(float, default=0.0)
    time_points = Optional(FloatArray)
    data_points = Optional(FloatArray)
    from_channel = Required(Channel)
    to_hub = Optional("SensorHub")

class SensorHub(db.Entity):
    ser_no = PrimaryKey(int)
    name = Required(str)
    channels = Set(ChannelData)
    

# Helper data structures:

@dataclass
class SensorData():
    """ Dataclass for passing sensor-data around outside DB """
    hub_name: str = str()
    hub_id: int = 0
    ch_name: str = str()
    ch_desc: str = str()
    ch_id: int = int()
    unit: str = str()
    start_datetime: float = 0.0
    data: list = field(default_factory=list)    # List of time-val, sample-val tuples

    @property
    def sensor_data(self):
        """ Split data-tuples into separate lists """
        time_values = list()        # List of time-point values
        sensor_values = list()      # List of sample values
        for t, v in self.data:
            time_values.append(t)
            sensor_values.append(v)
        return time_values, sensor_values
    
    def info(self):
        print("================================================================")
        print("Sensor-data INFO")
        print("================================================================")
        print(f"Hub name: {self.hub_name}")
        print(f"Hub ID: {self.hub_id}")
        print(f"Channel name: {self.ch_name}")
        print(f"Description: {self.ch_desc}")
        print(f"Channel ID: {self.ch_id}")
        print(f"START-time (first sample): {datetime.fromtimestamp(self.start_datetime)}")

    def show(self):
        self.info()
        #
        print("----------------------------------------------------------------")
        print("Data:")
        for time_val, sample_val in self.data:
            #time_val, sample_val = tv_pair
            # Get Epoch-time (i.e. 'absolute' time) from START-time + delta-time:
            absolute_date_time = self.start_datetime + time_val
            #
            print(f"DateTime: {datetime.fromtimestamp(absolute_date_time)}\t\tValue = {sample_val:.3f} {self.unit}")
        print("----------------------------------------------------------------\n")

    def get(self):
        return asdict(self)


# Helper functions:

def plot_time_series(t_values, y_values, title: str = "Time-series Plot", xlabel: str = 'DeltaTime', ylabel: str = 'Value', 
                    color: str = 'tab:red', x_relative_size: int = 16, y_relative_size: int = 5, resolution_dpi: int = 100):
    plt.figure(figsize=(x_relative_size, y_relative_size), dpi=resolution_dpi)
    plt.plot(t_values, y_values, color=color)
    plt.ylim(0, 100)
    plt.gca().set(title=title, xlabel=xlabel, ylabel=ylabel)
    plt.show()


# *************************************************** DB 'STORE' functions ************************************************************* 

# Create sensor entities:
@db_session
def create_channels_and_hubs():
    bma380_temp = Channel(name="BMA380_temp", si_unit="°C", description="BMA380 temperature reading")
    adxl255_accel = Channel(name="ADXL255_accel")
    fxs3008_pressure = Channel(name="FXS3008_pressure", si_unit="Bar")
    bma380_humidity = Channel(name="BMA380_humidity", si_unit="%", description="BMA380 humidity reading")
    # Then sensor-hub entities ...
    SensorHub(ser_no=123, name="TestHub1", channels=(ChannelData(from_channel=bma380_temp)))
    SensorHub(ser_no=223, name="TestHub2", channels=(ChannelData(from_channel=bma380_temp), ChannelData(from_channel=adxl255_accel)))
    SensorHub(ser_no=323, name="TestHub3", channels=(ChannelData(from_channel=bma380_temp), ChannelData(from_channel=fxs3008_pressure)))
    SensorHub(ser_no=533, name="TestHub4", channels=(ChannelData(from_channel=bma380_humidity)))


# Create a single SensorHub entity
@db_session
def create_sensor_hub(hub_name: str, ser_no: int, ch_names: list) -> None:
    # Create SET of 'ChannelData' instances:
    ch_data_set = set()
    for ch_name in ch_names:
        try:
            ch_data = ChannelData(from_channel=Channel[ch_name])
            if ch_data:
                ch_data_set.add(ch_data)
            else:
                print(f"ChannelData-instance w. ch-name '{ch_name}' NOT found!")
        except Exception as ex:
            print(f"Query for ChannelData-instance w. name '{ch_name}' exploded! Reason: {ex}")
    #
    # SensorHub(ser_no=ser_no, name=hub_name, channels=( set([ChannelData(from_channel=Channel[ch_name]) for ch_name in ch_names]) ) )
    #
    # Create instance:
    SensorHub(ser_no=ser_no, name=hub_name, channels=ch_data_set)   


@db_session
def add_data_to_hub(id: int = -1, ch_name: str = None, tsd: list = None) -> None:
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
    channel_query = hub.channels.select(lambda cd: cd.from_channel.name == ch_name)
    channel = channel_query.first()
    if channel:
        if channel.start_time == 0:
            channel.start_time = time.time()
        for ts_point in tsd:
            time_point, data_point = ts_point
            channel.time_points.append(channel.start_time - time_point)     # Store delta-time = offset from START-time!
            channel.data_points.append(data_point)
        print(f"Added {len(tsd)} data-points to channel '{ch_name}' of hub entity {id} named '{hub.name}' ...\n")
    else:
        print(f"ERROR: channel named '{ch_name}' NOT found! Could not add data ...\n")


# *************************************************** DB 'LOAD' functions ************************************************************* 

# Retrieve from DB:
@db_session
def get_hubs_and_show_info():
    hubs = SensorHub.select(lambda hub: hub.ser_no)       # Retrieve ALL SensorHub-entitities
    num_hubs = len(hubs)
    print(f"All {num_hubs} SensorHub-entities:")
    print("------------------------------------------")
    for hub in hubs:
        print(f"Name = {hub.name}")
        print(f"SerNo = {hub.ser_no}")
        if 0 == len(hub.channels):
            print("No channels??")
        else:
            print("Channels:")
            for ch in hub.channels:
                print(f"\t{ch.from_channel.name}")
        print("------------------------------------------")
    #
    print("\n")


@db_session
def show_data_from_hub(id: int = -1, ch_name: str = None) -> None:
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
    found_channel = False
    for channel in hub.channels:
        # Get associated channel-data's channel name:
        current_channel_name = channel.from_channel.name
        if ch_name:
            # If a specific name is given, show data ONLY from this channel - else show all channels:
            if current_channel_name != ch_name:
                continue
            else:
                found_channel = True
        else:
            found_channel = True
        # Get channel SI-unit
        unit = channel.from_channel.si_unit
        x_vals = channel.time_points
        y_vals = channel.data_points
        num_time_values = len(x_vals)
        num_data_values = len(y_vals)
        if num_time_values == 0:
            print(f"WARN: no data for channel '{current_channel_name}'...")
            continue
        if num_time_values != num_data_values:
            print(f"ERROR: data inconsistency - {num_time_values} time values != {num_data_values} data values!! Cannot show data for channel '{current_channel_name}'...")
            continue
        # Show data:
        print(f"\nChannel {current_channel_name} (description: '{channel.from_channel.description}') data:")
        print("-------------------------------------------------------------------------------------------------")
        for idx in range(num_time_values):
            print(f"Sample {idx}: time = {x_vals[idx]:.3f}, value = {y_vals[idx]:.3f} {unit}")
        print("-----------------------------------------------------------------------------------------------\n")
    #
    if not found_channel:
        print(f"INFO: did not find channel named '{ch_name}'!")


@db_session
def get_sensor_data(hub_id: int = -1, ch_name: str = None) -> None:
    hub = None
    if hub_id < 0:
        print("Invalid ID given! Cannot proceed ...")       # Redundant - will be caught by exception-check below anyway, but OK here ...
        return None
    # Get hub:
    try:
        hub = SensorHub[hub_id]    
        if hub is None:
            print(f"No 'SensorHub' entity w. ID {id} found!! ID={id} non-existent!")            
            return          
    except Exception as ex:
        print(f"Query for 'SensorHub' entity w. ID {id} exploded!! Resaon: {ex}")
        return
    #
    # Get channel:
    channel_query = hub.channels.select(lambda cd: cd.from_channel.name == ch_name)
    channel = channel_query.first()
    if channel:
        print(f"Got {len(channel.data_points)} data-points from channel '{ch_name}' of hub entity {id} named '{hub.name}' ...\n")
    else:
        print(f"ERROR: channel named '{ch_name}' NOT found! Could not GET sensor-data ...\n")
        return None
    # Get channel attributes:
    unit = channel.from_channel.si_unit
    description = channel.from_channel.description 
    start_time = channel.start_time
    ch_id = channel.ch_id
    x_vals = channel.time_points
    y_vals = channel.data_points
    # Make data-tuple:
    time_series_data = list(zip(x_vals, y_vals))    # TODO: make an additional 'TimeSeriesDataPoint' dataclass?
    #
    return SensorData(hub_name=hub.name, hub_id=hub_id, ch_name=ch_name, ch_desc=description, ch_id=ch_id, unit=unit, start_datetime=start_time, data=time_series_data)


# ******************************************************* Test-helpers: ********************************************************************

def generate_dummy_data(num_samples: int = 10, min_val: int = -100, max_val: int = 100, factor: float = 0.025) -> list:
    time_points = list()
    data_points = list()
    #
    for _ in range(num_samples):
        time_point = time.time()
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


def fix_gc_setup():
    """
    Fixes setup of Python's GarbageCollector('gc') - improves run of smaller applications - but startup may take a little longer.
    """
    import gc
    # Clean up what might be garbage so far.
    gc.collect(2)
    # Exclude current items from future GC.
    gc.freeze()
    #
    allocs, gen1, gen2 = gc.get_threshold()
    allocs = 50_000  # Start the GC sequence every 50K not 700 allocations.
    gen1 = gen1 * 2
    gen2 = gen2 * 2
    gc.set_threshold(allocs, gen1, gen2)


# ***************************** FUNCTIONAL TEST ******************************************

if __name__ == "__main__":
    fix_gc_setup()
    #
    # Create database tables (required before calling 'db_session' functions):
    db.generate_mapping(create_tables=True)
    # Fill DB w. stuff ...
    create_channels_and_hubs()
    create_sensor_hub(hub_name="BasicHub", ser_no=666, ch_names=['BMA380_temp', 'ADXL255_accel', 'FXS3008_pressure'])
    create_sensor_hub(hub_name="BasicHub", ser_no=777, ch_names=['ADXL255_accel', 'FXS3008_pressure', 'BMA380_temp'])
    #
    get_hubs_and_show_info()
    # Add TEMP-data:
    ts_data = generate_dummy_data()
    add_data_to_hub(id=777, ch_name='BMA380_temp', tsd=ts_data)
    # Check 1:
    show_data_from_hub(id=777)
    show_data_from_hub(id=777, ch_name='BMA380_temp')       # OK
    # Check 2:
    show_data_from_hub(id=533, ch_name='BMA380_humidity')   # OK --> but no data
    # 
    # Add TEMP-data:
    ts_data = generate_dummy_data(num_samples=50, min_val=30, max_val=40, factor=0.99)
    add_data_to_hub(id=533, ch_name='BMA380_humidity', tsd=ts_data)
    # Check 3:
    show_data_from_hub(id=533, ch_name='BMA380_humidity')   # OK --> has data now ...
    # Check 4:
    show_data_from_hub(id=533, ch_name='BMA280_temp')       # Should FAIL! (non-existent channel-name ...)
    #
    # Test 'get_sensor_data()':
    UUT = get_sensor_data(hub_id=533, ch_name='BMA380_humidity')
    UUT.show()
    sensor_ch_info = UUT.get()
    print()
    print(sensor_ch_info)
    print()
    print(f"Channel info: {sensor_ch_info.get('ch_desc')}")
    #
    # Finalize
    db.disconnect()
    #
    # And - for fun - plot data ...
    plot_title = f"Sensor-data from hub {sensor_ch_info.get('hub_id')}, named '{sensor_ch_info.get('hub_name')}': channel = '{sensor_ch_info.get('ch_name')}'"
    plot_legend = f"{sensor_ch_info.get('ch_desc')} - in [{sensor_ch_info.get('unit')}]"
    sensor_data = sensor_ch_info.get('data')
    #
    tv, dv = UUT.sensor_data
    #
    plot_time_series(t_values=tv, y_values=dv, title=plot_title, ylabel=plot_legend)


