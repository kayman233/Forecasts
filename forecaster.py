# -*- coding: utf-8 -*-

import datetime
import math


class Forecaster:
    def __init__(self, date, first):
        self.current_date = date
        self.deviation_list = []
        self.first_day = first
        self.date_format = "%Y-%m-%d"
        self.time_format = "%H:%M"
        self.closest_difference = 5400

    def get_time_difference(self, first, second):
        if first is None or second is None:
            return 0
        first_time = datetime.datetime.strptime(first[:5], self.time_format)
        second_time = datetime.datetime.strptime(second[:5], self.time_format)
        diff1 = first_time - second_time
        diff2 = second_time - first_time
        return min(diff1.seconds, diff2.seconds) # не очень понял, почему тут минимум, а не модуль

    def get_previous_forecasts(self, cur, day, difference):
        cur.execute("""
                            SELECT real_weather.day_of_insert, real_weather.temperature, forecasts.temperature,
                            forecasts.forecast_api, forecasts.day_of_insert, 
                            real_weather.time_of_insert, forecasts.forecast_time
                            FROM real_weather
                            JOIN forecasts ON real_weather.day_of_insert = forecasts.forecast_day
                            WHERE real_weather.day_of_insert = ? AND 
                                  forecasts.day_of_insert = date(real_weather.day_of_insert,?);""",
                    [day, difference])

    def day_increase(self, day, i):
        date = datetime.datetime.strptime(day, self.date_format)
        date = date + datetime.timedelta(days=i)
        day_and_time = str(date).split(' ')
        return day_and_time[0]

    def get_deviation_list(self, cur):

        for i in range(1, 6):
            owp_sum = 0 # если захочешь добавить еще один сервис для сравнения, то придется копипастить переменные и тп, лучше сделать массив обьектов типа [{id: 'owp', sum: 0, cnt: 0}, {id: 'meta', sum: 0, cnt: 0}] ну или name вместо id
            owp_cnt = 0
            meta_sum = 0
            meta_cnt = 0

            day = self.day_increase(self.first_day, i)
            difference = str(0 - i) + ' day'

            while day < self.current_date:

                self.get_previous_forecasts(cur, day, difference)
                day = self.day_increase(day, 1)

                rows = cur.fetchall()
                for row in rows:
                    real_day_of_insert, real_temperature, forecast_temperature, \
                    api, forecast_day_of_insert, real_time, forecast_time = row

                    if self.get_time_difference(real_time, forecast_time) < self.closest_difference:
                        if api == 'OWP':
                            owp_sum += abs(real_temperature - forecast_temperature) ** 2
                            owp_cnt += 1
                        else:
                            meta_sum += abs(real_temperature - forecast_temperature) ** 2
                            meta_cnt += 1

            if owp_cnt > 1:
                owp_deviation = math.sqrt(owp_sum / (owp_cnt - 1))
            else:
                owp_deviation = math.sqrt(owp_sum)

            if meta_cnt > 1:
                meta_deviation = math.sqrt(meta_sum / (meta_cnt - 1))
            else:
                meta_deviation = math.sqrt(meta_sum)

            self.deviation_list.append([owp_deviation, meta_deviation])

    @staticmethod
    def print_forecast(day, min_temp, max_temp):
        print(day + ': ' + str(min_temp) + '°' + '...' + str(max_temp) + '°')

    def get_day_forecast(self, cur, difference):

        cur.execute(""" SELECT forecasts.temperature, forecasts.forecast_api,
                                            forecasts.forecast_day, forecasts.forecast_time
                                    FROM forecasts
                                    WHERE forecasts.day_of_insert = $1 AND forecasts.forecast_day = date($1, $2);""",
                    [self.current_date, difference])

    def get_forecast(self, cur, number_of_days):

        self.get_deviation_list(cur)
        if number_of_days > 5:
            print("It's too hard to predict for so many days")
            number_of_days = 5

        day = self.day_increase(self.current_date, 1)
        for i in range(1, number_of_days + 1):
            difference = str(i) + ' day'

            self.get_day_forecast(cur, difference)
            rows = cur.fetchall()

            owp_avg_temp = 0
            meta_temp = 0
            cnt = 0

            for row in rows:
                forecast_temp, api, date, forecast_time = row

                if forecast_time is not None and '12:00:00' <= forecast_time <= '18:00:00':
                    cnt += 1
                    owp_avg_temp = (owp_avg_temp * (cnt - 1) + forecast_temp) / cnt
                else:
                    if forecast_time is None:
                        meta_temp = forecast_temp

            min_temp = int(min(owp_avg_temp - self.deviation_list[0][0], meta_temp - self.deviation_list[0][1]))
            max_temp = int(max(owp_avg_temp + self.deviation_list[0][0], meta_temp + self.deviation_list[0][1]))

            self.print_forecast(day, min_temp, max_temp)
            day = self.day_increase(day, 1)
