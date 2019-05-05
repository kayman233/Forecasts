import pytest
import sqlite3
import sys
import datetime
sys.path.append('../')
from adder import Adder, ApiException


def test_adder_unreal_temp():
    adder = Adder('2000-06-13', '22:00:00')
    conn = sqlite3.connect('src/weather.db')

    with pytest.raises(ValueError):
        adder.add_real_weather(conn, '+1000000000000000')


def test_adder_incorrect_input_temp_1():
    adder = Adder('2000-06-13', '22:00:00')
    conn = sqlite3.connect('src/weather.db')

    with pytest.raises(ValueError):
        adder.add_real_weather(conn, 'abc')


def test_adder_incorrect_input_temp_2():
    adder = Adder('2000-06-13', '22:00:00')
    conn = sqlite3.connect('src/weather.db')

    with pytest.raises(ValueError):
        adder.add_real_weather(conn, '+2q')


def test_adder_owp():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    add = Adder(current_date, '22:00:00')
    conn = sqlite3.connect('src/weather.db')
    add.add_owp_forecasts(conn)


def test_adder_meta():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    add = Adder(current_date, '22:00:00')
    conn = sqlite3.connect('src/weather.db')
    add.add_meta_weather_forecasts(conn)


def test_adder_owp_stress():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    for i in range(0, 200):
        add = Adder(current_date, '22:00:00')
        conn = sqlite3.connect('src/weather.db')
        add.add_owp_forecasts(conn)


def test_adder_meta_stress():
    now = datetime.datetime.now()
    date_time = str(now).split(' ')

    current_date = date_time[0]

    for i in range(0, 100):
        add = Adder(current_date, '22:00:00')
        conn = sqlite3.connect('src/weather.db')
        add.add_meta_weather_forecasts(conn)

