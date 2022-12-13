from fastapi import FastAPI
from pony.orm import db_session, set_sql_debug
from models import db, Channel
from fast_pony_crud import create_crud_routes
import uvicorn
import os


USE_API_KEY = False
#
if USE_API_KEY:
    API_TEST_KEY = "test123"
else:
    API_TEST_KEY = None


# FastAPI app object:
app = FastAPI()

# DB connection:
database_url = os.environ.get('DATABASE_URL')      # If NOT set (i.e. 'None' returned), use SQLite file as DB.
if database_url:
    db.bind(provider='postgres', dsn=database_url)
else: 
    db.bind(provider='sqlite', filename='sensorhub_db.sqlite', create_db=True)

# Map model-classes to tables, and - create tables in DB:
db.generate_mapping(create_tables=True)



@db_session
def add_channels() -> None:
    """ Just add some 'Channel'-instances """
    bma280_temp = Channel(name="bma280_temp", description="BMA280 temp reading", si_unit="Celcius")     # Not really a SI-unit but compatible (w. Kelvin) ...
    sht721_hygro = Channel(name="sht721_hygro", description="SHT721 humidity reading", si_unit="%RH")   # Not really a SI-unit whatsoever, butbut ...
    adxl355_accel = Channel(name="adxl355_accel", description="ADXL355 accel reading", si_unit="G") 
    # Write to DB:
    db.commit()


# ****************************** Run API server ********************************
if __name__ == "__main__":
    add_channels()
    #
    create_crud_routes(db, app, prefix="/db", api_key="test123")
    #
    # 'uvicorn' will automatically refresh API whenever code changes in folder!
    uvicorn.run(app, port=8889)

