"""
@brief Demo of 'timezone' std.library, used to generate time-zone info.

@note Requires >= Python3.9 !
"""

from zoneinfo import ZoneInfo
from datetime import datetime


def show_datetime_info(dt_info: tuple, tz: str = None):
    if tz is None:
        print("No TimeZone info ...")
        # Fallback 1:
        dt = datetime(year, month, day, hour)
    else:
        try:
            tzInfo = ZoneInfo(tz)
            dt = datetime(year, month, day, hour, tzinfo=tzInfo)
        except Exception as ex:
            print(f"ERROR! Cause: {ex}")
            # Fallback 2:
            dt = datetime(year, month, day, hour)
    #
    print(f"DateTime: {dt}")
    tzName = dt.tzname()
    print(f"""TimeZone name: {tzName if tzName else "no TZ-name"}""")
    #
    print()


if __name__ == "__main__":
    year = 2022
    month = 10
    day = 31
    hour = 12
    dt_info = year, month, day, hour
    #
    show_datetime_info(dt_info=dt_info)
    #
    show_datetime_info(dt_info=dt_info, tz="America/Los_Angeles")
    #
    show_datetime_info(dt_info=dt_info, tz="Europe/Oslo")
    #
    show_datetime_info(dt_info=dt_info, tz="Luna/SeaOfTranquility")

