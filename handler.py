import sqlite3
import datetime

import adder
import forecaster


class Handler:
    def __init__(self):
        now = datetime.datetime.now()
        date_time = str(now).split(' ')

        self.current_date = date_time[0]
        self.current_time = date_time[1]

        self.get_commands = ['get', 'show', 'Get', 'Show']
        self.add_commands = ['Add', 'add']

        self.conn = sqlite3.connect('src/weather.db')
        self.cur = self.conn.cursor()

        self.adder = adder.Adder(self.current_date, self.current_time)

        self.cur.execute("SELECT min(real_weather.day_of_insert) FROM real_weather")
        first_day = self.cur.fetchall()[0][0]

        self.forecaster = forecaster.Forecaster(self.current_date, first_day)

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
        if commands[0] in self.get_commands:
            if len(commands) > 3 or commands[3] == 'tomorrow':

                if commands[3] == 'tomorrow':
                    number_of_days = 1
                else:
                    number_of_days = int(commands[3])
                self.forecaster.get_forecast(self.cur, number_of_days)

            else:
                raise ValueError
        elif commands[0] in self.add_commands:
            add_str = ' '.join(commands[1:])

            if not self.has_today_forecast():
                self.adder.add_real_weather(self.conn, add_str)
                self.adder.add_forecasts(self.conn)
            else:
                raise Exception
