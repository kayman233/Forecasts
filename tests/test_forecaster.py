import pytest
import sqlite3
import sys
sys.path.append('../')
from forecaster import Forecaster, ApiInfo, ForecasterException


def test_day_increase_1():
    forecaster = Forecaster('2000-06-13', '2000-06-13', 5)
    assert forecaster.day_increase('2000-06-13', 1) == '2000-06-14'


def test_day_increase_n():
    forecaster = Forecaster('2000-06-13', '2000-06-13', 5)
    assert forecaster.day_increase('2000-06-13', 30) == '2000-07-13'


def test_time_difference_none():
    forecaster = Forecaster('2019-05-04', '2019-04-21', 5)
    assert forecaster.get_time_difference(None, 5) == 0


def test_time_difference_hour():
    minute = 60
    forecaster = Forecaster('2019-05-04', '2019-04-21', 5)
    assert forecaster.get_time_difference('13:30:00', '14:30:00') == 60 * minute


def test_get_forecast_exception():
    conn = sqlite3.connect('src/weather.db')
    cur = conn.cursor()

    forecaster = Forecaster('2019-05-04', '2019-04-21', 5)
    with pytest.raises(ForecasterException):
        forecaster.get_forecast(cur)


def test_get_forecast():
    conn = sqlite3.connect('src/weather.db')
    cur = conn.cursor()

    forecaster = Forecaster('2019-05-01', '2019-04-21', 5)
    assert len(forecaster.get_forecast(cur)) > 0


def test_api_info_on_zero():
    info = ApiInfo()
    assert info.calculate_deviation() == 0
