"""
@file models.py

DB model of cyper-physical system w. sensors(IN-values) and actuators(OUT-values), where
- IN/OUT-channels are represented by 'Channel'-model; a sensor can have multiple channels (e.g. a 10-DOF IMU)
- each channel link to data modeled as 'ChannelData' objects, with linked 'Channel' providing a description of what data is produced by channel
- and data from one or multiple sensor channels end up in a 'SensorHub' model instance
This makes it easy to connect channels to a sensor-hub, and to tap data from one channel, multiple channels, or all.
Included in 'Channel' model is 
- a description of the channel, e.g. "BMA280_temp"
- whether it is an input (i.e. sensor) or output (i.e. actuator) --> allows for validation when doing WRITE or READ on linked 'ChannelData' instance
- unit of measure (preferrably SI-unit) --> as UTF-8 string
- other (extensible), mostly optional attributes --> e.g. no of bits (may be useful), sampling frequency (internal in sensor or actuator) etc.

"""

from pony.orm import Database, PrimaryKey, Required, Optional, Set, db_session, set_sql_debug, FloatArray
from pydantic.dataclasses import dataclass
from pydantic import ConstrainedList, validator


db = Database()

# Config

class Config:
    arbitrary_types_allowed = True
    check_fields=False


# Models:

class Channel(db.Entity):
    ch_id = PrimaryKey(int, auto=True)
    name = Required(str)
    is_output = Optional(bool, default=False)
    description = Optional(str, default="<sensor IN-type>" if is_output else "<actuator OUT-type>")
    si_unit = Optional(str, default="<unitless>")
    scale_factor = Optional(float, default=1.0)
    sample_freq = Optional(float, default=1.0)    # --> Hz
    num_bits = Optional(int, default=16)          # --> TODO: relevant???
    ch_data_sources = Set("ChannelData")

"""
@dataclass(config=Config)
class ChannelData(db.Entity):
    ch_id = PrimaryKey(int, auto=True)
    start_time = Optional(float, default=0.0)
    time_points = Optional(FloatArray)
    data_points = Optional(FloatArray)
    from_channel = Required(Channel)
    to_hub = Optional("SensorHub")

    @validator('time_points', check_fields=False)
    def time_point_is_floatarray(cls, v):
        assert isinstance(v, FloatArray), 'must be (PonyORM-)type FloatArray'
        return v

    @validator('data_points', check_fields=False)
    def data_point_is_floatarray(cls, v):
        assert isinstance(v, FloatArray), 'must be (PonyORM-)type FloatArray'
        return v
"""
class ChannelData(db.Entity):
    data_id = PrimaryKey(int, auto=True)
    time_point = Optional(float, default=0.0)
    data_point = Optional(float, default=0.0)
    from_channel = Required(Channel)
    to_hub = Optional("SensorHub")

class SensorHub(db.Entity):
    ser_no = PrimaryKey(int)
    name = Required(str)
    channels = Set(ChannelData)
    


