# -*- coding: utf-8 -*-

import datetime
import math


class Forecaster:
    def __init__(self, date, first):
        self.current_date = date
        self.deviation_list = []
        self.first_day = first
        self.today_date = datetime.datetime.strptime(self.current_date, "%Y-%m-%d") # формат у тебя повторяется, лучше вынести в константу

    @staticmethod
    def get_time_difference(first, second):
        if first is None or second is None:
            return 0
        first_time = datetime.datetime.strptime(first[:5], "%H:%M")
        second_time = datetime.datetime.strptime(second[:5], "%H:%M")
        diff1 = first_time - second_time
        diff2 = second_time - first_time
        return min(diff1.seconds, diff2.seconds) # не очень понял, почему тут минимум, а не модуль

    def get_deviation_list(self, cur):

        for i in range(1, 6):
            owp_sum = 0 # если захочешь добавить еще один сервис для сравнения, то придется копипастить переменные и тп, лучше сделать массив обьектов типа [{id: 'owp', sum: 0, cnt: 0}, {id: 'meta', sum: 0, cnt: 0}] ну или name вместо id
            owp_cnt = 0
            meta_sum = 0
            meta_cnt = 0

            date = datetime.datetime.strptime(self.first_day, "%Y-%m-%d")
            date = date + datetime.timedelta(days=i)
            day = str(date).split(' ')

            difference = str(0 - i) + ' day'

            while day[0] < self.current_date: # что за day[0]? у тебя разве где-то есть day[1], чтобы хранить весь day?
                # Лучше это как-то назвать, иначе приходится вчитываться, что же тут вызывается и с какими параметрами
                cur.execute("""
                    SELECT real_weather.day_of_insert, real_weather.temperature, forecasts.temperature,
                    forecasts.forecast_api, forecasts.day_of_insert, 
                    real_weather.time_of_insert, forecasts.forecast_time
                    FROM real_weather
                    JOIN forecasts ON real_weather.day_of_insert = forecasts.forecast_day
                    WHERE real_weather.day_of_insert = ? AND 
                          forecasts.day_of_insert = date(real_weather.day_of_insert,?);""",
                             [day[0], difference])

                date = datetime.datetime.strptime(day[0], "%Y-%m-%d")
                date = date + datetime.timedelta(days=1)
                day = str(date).split(' ')

                rows = cur.fetchall()
                for row in rows:
                    real_day_of_insert, real_temperature, forecast_temperature, \
                    api, forecast_day_of_insert, real_time, forecast_time = row

                    if self.get_time_difference(real_time, forecast_time) < 5400: # опять магическая константа
                        if api == 'OWP':

                            owp_sum += abs(real_temperature - forecast_temperature) ** 2
                            owp_cnt += 1
                        else:
                            meta_sum += abs(real_temperature - forecast_temperature) ** 2
                            meta_cnt += 1

            if owp_cnt > 2: # что значит эта 2?
                owp_deviation = math.sqrt(owp_sum / (owp_cnt - 1))
            else:
                owp_deviation = math.sqrt(owp_sum)

            if meta_cnt > 2:
                meta_deviation = math.sqrt(meta_sum / (meta_cnt - 1))
            else:
                meta_deviation = math.sqrt(meta_sum)

            self.deviation_list.append([owp_deviation, meta_deviation])

    def get_forecast(self, cur, number_of_days):

        self.get_deviation_list(cur)
        if number_of_days > 5:
            print("It's too hard to predict")
            number_of_days = 5
        for i in range(1, number_of_days + 1):
            difference = str(i) + ' day'

            cur.execute(""" SELECT forecasts.temperature, forecasts.forecast_api,
                                    forecasts.forecast_day, forecasts.forecast_time
                            FROM forecasts
                            WHERE forecasts.day_of_insert = $1 AND forecasts.forecast_day = date($1, $2);""",
                        [self.current_date, difference])

            rows = cur.fetchall()

            owp_avg_temp = 0
            meta_temp = 0
            cnt = 0

            avg = []

            for row in rows:
                forecast_temp, api, date, forecast_time = row

                if api == 'OWP' and '12:00:00' <= forecast_time <= '18:00:00': # лучше не завязываться на названиях
                    avg.append([forecast_time, forecast_temp])
                    cnt += 1
                    owp_avg_temp = (owp_avg_temp * (cnt - 1) + forecast_temp) / cnt
                else:
                    if api != 'OWP':
                        meta_temp = forecast_temp

            date = self.today_date + datetime.timedelta(days=i)
            day = str(date).split(' ')

            min_temp = int(min(owp_avg_temp - self.deviation_list[0][0], meta_temp - self.deviation_list[0][1]))
            max_temp = int(max(owp_avg_temp + self.deviation_list[0][0], meta_temp + self.deviation_list[0][1]))
            print(day[0] + ': ' + str(min_temp) + '°' + '...' + str(max_temp) + '°')
