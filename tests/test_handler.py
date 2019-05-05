import pytest
import sqlite3
import sys

sys.path.append('../')
from handler import Handler, AdderException, ForecastException


def delete_inserts(conn, day):
    conn.execute('''delete from real_weather where day_of_insert == ?''', [day])
    conn.execute('''delete from forecasts where day_of_insert == ?''', [day])
    conn.commit()


def test_info_print_1(capfd):
    handler = Handler()
    handler.print_info()
    out, err = capfd.readouterr()
    assert out == "Add current weather\n"


def test_info_print_2(capfd):
    handler = Handler()
    conn = sqlite3.connect('src/weather.db')

    handler.adder.add_real_weather(conn, '+10')

    handler.print_info()
    out, err = capfd.readouterr()
    assert "You have already added weather today\n" in out

    delete_inserts(conn, handler.current_date)


def test_get_command_exception():
    handler = Handler()

    with pytest.raises(ForecastException):
        handler.get_command('get forecast for 5 days')


def test_get_first_day():
    handler = Handler()

    assert handler.get_first_day() == '2019-04-21'


def test_print_null(capfd):
    handler = Handler()

    handler.print_forecasts(5)
    out, err = capfd.readouterr()
    assert out == ""


def test_adder_exception():
    handler = Handler()
    conn = sqlite3.connect('src/weather.db')

    handler.adder.add_real_weather(conn, '+10')

    with pytest.raises(AdderException):
        handler.get_command('add +15')

    delete_inserts(conn, handler.current_date)
