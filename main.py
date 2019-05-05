import handler


if __name__ == "__main__":
    hand = handler.Handler()
    hand.print_info()
    while True:
        command = str(input())
        try:
            hand.get_command(command)
        except (ValueError, handler.InputException):
            print('Try one more time')
        except handler.AdderException:
            print('Already added')
            print('Try tomorrow')
        except handler.ForecastException:
            print('Firstly add current weather')
        except handler.APIException:
            print('Problems with servers, try later')
        except handler.DecodingException:
            print('Problems with decoding data, try later')
