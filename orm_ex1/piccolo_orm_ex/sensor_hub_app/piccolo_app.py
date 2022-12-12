"""
Import all of the Tables subclasses in your app here, and register them with
the APP_CONFIG.
"""

import os
from fastapi import FastAPI
from piccolo_api.fastapi.endpoints import FastAPIWrapper
from piccolo_api.crud.endpoints import PiccoloCRUD
from starlette.routing import Mount, Router

from piccolo.conf.apps import AppConfig

# Import DB-entity models:
from tables import (
    Channel,
    ChannelData,
    SensorHub,
)


USE_FASTAPI = True

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="sensor_hub_app",
    migrations_folder_path=os.path.join(
        CURRENT_DIRECTORY, "piccolo_migrations"
    ),
    table_classes=[Channel, ChannelData, SensorHub],
    migration_dependencies=[],
    commands=[],
)

if USE_FASTAPI:
    # *********************************** FastAPI """ part *****************************************

    app = FastAPI()

    # Endpoints:

    FastAPIWrapper(
        root_url="/api/Channel",
        fastapi_app=app,
        piccolo_crud=PiccoloCRUD(
            table=Channel,
            read_only=False,
        )
    )

    FastAPIWrapper(
        root_url="/api/channel_data",
        fastapi_app=app,
        piccolo_crud=PiccoloCRUD(
            table=ChannelData,
            read_only=False,
        )
    )

    FastAPIWrapper(
        root_url="/api/sensor_hub",
        fastapi_app=app,
        piccolo_crud=PiccoloCRUD(
            table=SensorHub,
            read_only=False,
        )
    )
else:
    # ****************************** PiccoloCRUD part *********************************
    app = Router([
    Mount(
        path='/api/channel',
        app=PiccoloCRUD(table=Channel, read_only=False),
    ),
    Mount(
        path='/api/channel_data',
        app=PiccoloCRUD(table=ChannelData, read_only=False),
    ),
    Mount(
        path='/api/sensorhub',
        app=PiccoloCRUD(table=SensorHub, read_only=False),
    ),
])


