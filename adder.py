import requests
import re
from urllib.parse import urljoin


class ForecastInfo:
    def __init__(self, date_, time_, temperature_):
        self.date = date_
        self.time = time_
        self.temperature = temperature_


class ApiException(Exception):
    """API exception"""
    pass


class DecodeException(Exception):
    """Decode exception"""
    pass


class Adder:
    def __init__(self, date, time):
        self.current_date = date
        self.current_time = time
        self.lower_bound = -80
        self.upper_bound = 60

    def add_real_weather(self, conn, user_input):
        temp_state = user_input

        current_temperature = int(temp_state)

        if current_temperature < self.lower_bound or current_temperature > self.upper_bound:
            raise ValueError

        conn.execute("INSERT INTO real_weather VALUES ($1, $2, $3)",
                     (self.current_date, self.current_time, current_temperature))

        conn.commit()

    def add_forecasts(self, conn):
        self.add_owp_forecasts(conn)
        self.add_meta_weather_forecasts(conn)
        conn.commit()

    def database_add(self, conn, api, forecast_date, forecast_time, forecast_temp):
        conn.execute('''
                                    INSERT INTO forecasts (forecast_api, day_of_insert, time_of_insert,
                                                           forecast_day, forecast_time, temperature)
                                    VALUES ($1, $2, $3, $4, $5, $6)''', (api, self.current_date, self.current_time,
                                                                      forecast_date, forecast_time, forecast_temp))

    def add_owp_forecasts(self, conn):
        forecasts_list = []

        with open('owp_api') as api_file:
            owp_api_id = api_file.read()

        city_id_owp = '524901'  # Moscow
        owp_url_base = 'http://api.openweathermap.org/data/2.5/forecast?'

        owp_params = {'id': city_id_owp, 'appid': owp_api_id, 'units': 'metric'}

        owp_response = requests.get(owp_url_base, params=owp_params)

        if re.match(r'2\d{2}', str(owp_response.status_code)) is None:
            raise ApiException

        owp_json_data = owp_response.json()

        for info in owp_json_data["list"]:
            forecast_date_time = str(info['dt_txt']).split(' ')
            forecast = ForecastInfo(forecast_date_time[0], forecast_date_time[1], info["main"]['temp'])
            forecasts_list.append(forecast)

        for forecast in forecasts_list:
            self.database_add(conn, 'OWP', forecast.date, forecast.time, forecast.temperature)

    def add_meta_weather_forecasts(self, conn):
        forecasts_list = []

        city_id_meta_weather = '2122265'  # Moscow
        meta_url_base = 'https://www.metaweather.com/api/location/'
        meta_weather_url = urljoin(meta_url_base, city_id_meta_weather)

        meta_weather_response = requests.get(meta_weather_url)

        if re.match(r'2\d{2}', str(meta_weather_response.status_code)) is None:
            raise ApiException

        try:
            meta_weather_json_data = meta_weather_response.json()
        except ValueError:  # if not JSON
            raise DecodeException

        try:
            for info in meta_weather_json_data['consolidated_weather']:
                forecast = ForecastInfo(info['applicable_date'], None, info['the_temp'])
                forecasts_list.append(forecast)
        except KeyError:
            raise DecodeException

        for forecast in forecasts_list:
            self.database_add(conn, 'Meta Weather', forecast.date, forecast.time, forecast.temperature)
