from fastapi import FastAPI
from models import db
from fast_pony_crud import create_crud_routes
import uvicorn
import os

app = FastAPI()

database_url = os.environ.get('DATABASE_URL')      # If NOT set (i.e. 'None' returned), use SQLite file as DB.
if database_url:
    db.bind(provider='postgres', dsn=database_url)
else: 
    db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

create_crud_routes(db,app,api_key="test")

if __name__ == "__main__":
    uvicorn.run(app)