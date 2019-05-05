import pytest
import sqlite3
import sys
import datetime
sys.path.append('../')
from adder import Adder


def test_adder_owp_stress():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    for i in range(0, 200):
        add = Adder(current_date, '22:00:00')
        conn = sqlite3.connect('src/weather.db')
        add.add_owp_forecasts(conn)
        conn.close()


def test_adder_meta_stress():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    for i in range(0, 100):
        add = Adder(current_date, '22:00:00')
        conn = sqlite3.connect('src/weather.db')
        add.add_meta_weather_forecasts(conn)
        conn.close()
