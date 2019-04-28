import handler


if __name__ == "__main__":
    hand = handler.Handler()
    while True:
        command = str(input())
        try:
            hand.get_command(command)
        except ValueError:
            print('Try one more time') #Почему еще раз попробовать?
        except handler.AdderException:
            print('Already added')
            print('Try tomorrow')
        except handler.ForecastException:
            print('Firstly add current weather')
