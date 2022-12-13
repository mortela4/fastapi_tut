"""
Import all of the Tables subclasses in your app here, and register them with
the APP_CONFIG.
"""

import os
from fastapi import FastAPI
from piccolo_admin.endpoints import create_admin
from piccolo_api.fastapi.endpoints import FastAPIWrapper
from piccolo_api.crud.endpoints import PiccoloCRUD
from piccolo.engine import engine_finder
from starlette.routing import Mount, Router

from piccolo.conf.apps import AppConfig

# Import DB-entity models:
from tables import Channel, ChannelData, SensorHub


USE_FASTAPI = True
USE_POSTGRESQL = False      # Default: use SQLite ...

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

    app = FastAPI( routes=[
                Mount("/admin/", create_admin(tables=APP_CONFIG.table_classes)),
            ],
        )

    # Endpoints:

    FastAPIWrapper(
        root_url="/api/channel/",
        fastapi_app=app,
        piccolo_crud=PiccoloCRUD(
            table=Channel,
            read_only=False,
        )
    )

    FastAPIWrapper(
        root_url="/api/channel_data/",
        fastapi_app=app,
        piccolo_crud=PiccoloCRUD(
            table=ChannelData,
            read_only=False,
        )
    )

    FastAPIWrapper(
        root_url="/api/sensor_hub/",
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


# *********************************** DB-connection part (if relevant) *************************************

if USE_POSTGRESQL:
    @app.on_event("startup")
    async def open_database_connection_pool():
        engine = engine_finder()
        await engine.start_connnection_pool()


    @app.on_event("shutdown")
    async def close_database_connection_pool():
        engine = engine_finder()
        await engine.close_connnection_pool()
