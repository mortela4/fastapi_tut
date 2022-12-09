"""
PiccoloORM example DB-entities.
"""

from piccolo.engine.sqlite import SQLiteEngine
#
from piccolo.table import Table
from piccolo.columns import ForeignKey, Integer, Varchar, Boolean, Float, Array

DB_NAME = "my_db.sqlite"

# Define DB to use:
DB = SQLiteEngine(path=DB_NAME)      # NOTE: should be in a "piccolo_conf.py" file!

# Models:

class Channel(Table):
    name = Varchar(length=100, primary_key=True)
    is_output = Boolean(default=False, required=False)
    description = Varchar(length=100, default="<sensor IN-type>" if is_output else "<actuator OUT-type>")
    si_unit = Varchar(length=100, default="<unitless>")
    scale_factor = Float(default=1.0)

class ChannelData(Table):
    ch_id = Integer(primary_key=True, auto_update=True)
    start_time = Float(default=0.0)
    time_points = Array(base_column=Float())
    data_points = Array(base_column=Integer())
    from_channel = ForeignKey(Channel)

class SensorHub(Table):
    ser_no = Integer(required=True)
    name = Varchar(length=100)
    channels = ForeignKey(references=ChannelData)
    

# **************************** Functional Test **********************************
if __name__ == "__main__":
    print(f"Creating SQLite database {DB_NAME} ...")

