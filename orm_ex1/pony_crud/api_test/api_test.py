"""
@file api_test.py

@brief Test of PonyORM-based database CRUD API - demonstrating use of POST/UPDATE/DELETE
"""

import json

from requests import get, post, update, put, delete, HTTPError, RequestException


API_PORT = 8889
API_NAME = "test_api"
API_VERSION = "1.0"

API_URL_ROOT = f"http://localhost:{API_PORT}/{API_NAME}"

API_URL_CHANNELS = f"{API_URL_ROOT}/channel"
API_URL_DATA = f"{API_URL_ROOT}/channel_data"
API_URL_HUBS = f"{API_URL_ROOT}/sensor_hub"

HUB_SER_NO_START = 1001


# ********************************* Helpers *****************************************

class ApiStatus():
    def __init__(self) -> None:
        self.status = HTTPError(status=400)
    def passed(self) -> bool:
        return False


# ***************************** Test Functions **************************************

# POST-functionality:

def add_hub(name: str, ser_no: int) -> ApiStatus:
    global HUB_SER_NO_START
    #
    HUB_SER_NO_START += 1   # Do this AFTER succesful POST-request!
    #
    pass


def add_channel(name: str, description: str) -> ApiStatus:
    pass


def add_data(name: str, description: str) -> ApiStatus:
    pass


# UPDATE functionality:

def update_hub(new_name: str, ser_no: int) -> ApiStatus:
    #
    pass


def update_channel(name: str, new_description: str) -> ApiStatus:
    pass


# DELETE functionality:
def delete_hub(ser_no: int) -> ApiStatus:
    pass


# ************************* API Functional Test *************************************
if __name__ == "__main__":
    pass

