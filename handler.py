import sqlite3
import datetime

import adder
import forecaster


class Handler:
    def __init__(self):
        self.conn = sqlite3.connect('src/weather.db')
        self.cur = self.conn.cursor()

        now = datetime.datetime.now()
        date_time = str(now).split(' ')

        self.current_date = date_time[0]
        self.current_time = date_time[1]
        self.first_day = self.get_first_day()

        self.get_commands = ['get', 'show', 'Get', 'Show'] # почему не сделать приведение в lowercase?
        self.add_commands = ['Add', 'add'] #Можно эти константы вынести из класса в приложение в папку constants и потом ide будет подсказывать написание, чтобы не сделать опечатку
        self.least_command_words = 3

        self.adder = adder.Adder(self.current_date, self.current_time)
        self.forecaster = forecaster.Forecaster(self.current_date, self.first_day)

    def get_first_day(self):
        self.cur.execute(
            "SELECT min(real_weather.day_of_insert) FROM real_weather")
        return self.cur.fetchall()[0][0]

    def has_today_forecast(self):
        self.cur.execute("""
                SELECT *
                FROM real_weather
                WHERE day_of_insert = $1
                """, [self.current_date])
        row = self.cur.fetchall()
        if len(row) == 0:
            return 0
        return 1

    def get_command(self, string):
        commands = string.split(' ')
        days_for_forecast = commands[3]
        if commands[0] in self.get_commands:
            if len(commands) > self.least_command_words or days_for_forecast == 'tomorrow':

                if commands[3] == 'tomorrow':
                    number_of_days = 1
                else:
                    number_of_days = int(commands[3])
                self.forecaster.get_forecast(self.cur, number_of_days)

            else:
                raise ValueError
        elif commands[0] in self.add_commands:
            add_str = ' '.join(commands[1:])

            if self.has_today_forecast():
                raise Exception
            else:
                self.adder.add_real_weather(self.conn, add_str)
                self.adder.add_forecasts(self.conn)
