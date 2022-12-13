"""
Piccolo-ORM config file.
"""

from piccolo.engine.sqlite import SQLiteEngine
from piccolo.conf.apps import AppRegistry


DB_NAME = "my_db.sqlite"

APP_REGISTRY = AppRegistry(
    apps=["home.sensor_hub_app", "piccolo_admin.sensor_hub_app"]
)


# Define DB to use:
DB = SQLiteEngine(path=DB_NAME)      
