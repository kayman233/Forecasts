import sqlite3
import datetime

import adder
import forecaster


class AdderException(Exception):
    """Adder exception"""
    pass


class ForecastException(Exception):
    """Forecaster exception"""
    pass


class InputException(Exception):
    """Input exception"""
    pass


class APIException(Exception):
    """API exception"""
    pass


class DecodingException(Exception):
    """Decoding exception"""
    pass


class Handler:
    def __init__(self):
        self.conn = sqlite3.connect('src/weather.db')
        self.cur = self.conn.cursor()

        now = datetime.datetime.now()
        date_time = str(now).split(' ')

        self.current_date = date_time[0]
        self.current_time = date_time[1]
        self.first_day = self.get_first_day()

        self.get_commands = ['get', 'show']
        self.add_commands = ['add']
        self.least_get_command_words = 3

        self.adder = adder.Adder(self.current_date, self.current_time)
        self.forecast_days_limit = 5
        self.forecaster = forecaster.Forecaster(self.current_date, self.first_day, self.forecast_days_limit )

        self.forecast_list = []

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

    def print_info(self):
        if self.has_today_forecast():
            print('You have already added weather today')
            print('Please ask me the forecast')
        else:
            print('Add current weather')

    def print_forecasts(self, number_of_days):
        for forecast in self.forecast_list[:number_of_days]:
            day = forecast[0]
            min_temp = forecast[1]
            max_temp = forecast[2]
            print(day + ': ' + str(min_temp) + '°' + '...' + str(max_temp) + '°')

    def get_command(self, string):
        commands = string.split(' ')

        if commands[0].lower() in self.get_commands:
            if len(commands) > self.least_get_command_words:
                days_for_forecast = commands[3]
            else:
                raise ValueError

            if days_for_forecast == 'tomorrow':
                number_of_days = 1
            else:
                number_of_days = int(commands[3])

            try:
                if len(self.forecast_list) == 0:
                    self.forecast_list = self.forecaster.get_forecast(self.cur)

                if number_of_days > self.forecast_days_limit:
                    print("It's too hard to predict for so many days")
                    number_of_days = 5

                self.print_forecasts(number_of_days)

            except forecaster.ForecasterException:
                raise ForecastException

        elif commands[0].lower() in self.add_commands:
            add_str = commands[1]

            if self.has_today_forecast():
                raise AdderException
            else:
                try:
                    self.adder.add_real_weather(self.conn, add_str)
                    self.adder.add_forecasts(self.conn)
                    print('Your data have been just added')
                except adder.ApiException:
                    raise APIException
                except adder.DecodeException:
                    raise
        else:
            raise InputException
