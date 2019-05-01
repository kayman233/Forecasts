import requests


class Adder:
    def __init__(self, date, time):
        self.current_date = date
        self.current_time = time

    def add_real_weather(self, conn, user_input):
        temp_state = user_input

        temperature_sign = temp_state[0]

        if temperature_sign == '-':
            current_temperature = 0 - int(temp_state[1:])
        elif temperature_sign == '+':
            current_temperature = int(temp_state[1:])
        else:
            current_temperature = int(temp_state)

        conn.execute("INSERT INTO real_weather VALUES (?, ?, ?)",
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
                                    VALUES (?, ?, ?, ?, ?, ?)''', (api, self.current_date, self.current_time,
                                                                      forecast_date, forecast_time, forecast_temp))

    def add_owp_forecasts(self, conn):
        forecasts_list = []

        owp_api_id_ = '97c122859f3196c90d736d7f9d3771fe'
        city_id_owp = '524901'  # Moscow

        owp_url = ''.join(['http://api.openweathermap.org/data/2.5/forecast?id=',
                           city_id_owp, '&appid=', owp_api_id_, '&units=metric'])
        owp_response = requests.get(owp_url)

        owp_json_data = owp_response.json()

        for info in owp_json_data["list"]:
            forecasts_list.append([info['dt_txt'], info["main"]['temp']])

        for forecast in forecasts_list:
            forecast_date_time = str(forecast[0]).split(' ')

            forecast_date = forecast_date_time[0]
            forecast_time = forecast_date_time[1]
            forecast_temp = forecast[1]
            self.database_add(conn, 'OWP', forecast_date, forecast_time, forecast_temp)

    def add_meta_weather_forecasts(self, conn):
        forecasts_list = []

        city_id_meta_weather = '2122265'  # Moscow

        meta_weather_url = ''.join(['https://www.metaweather.com/api/location/', city_id_meta_weather])
        
        meta_weather_response = requests.get(meta_weather_url)

        meta_weather_json_data = meta_weather_response.json()

        for info in meta_weather_json_data['consolidated_weather']:
            forecasts_list.append([info['applicable_date'], info['the_temp']])

        for forecast in forecasts_list:
            forecast_date = forecast[0]
            forecast_time = None
            forecast_temp = forecast[1]
            self.database_add(conn, 'Meta Weather', forecast_date, forecast_time, forecast_temp)
