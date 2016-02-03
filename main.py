import ast
import time
import random
import datetime
from tonybet import TonyBet
from topsport import TopSport
# from orakulas import Orakulas
# from xbet import Xbet

__author__ = 'Jonas Bajorinas'

# main parameters
params = dict()


# Automated betting control node
def play():
    # Local variables for bookmaker client control
    start_date = datetime.datetime.today().date()
    sessions_played = 0
    unusual_errors = 0
    connection_errors = 0
    sleep_time = params['sleep_time']

    while True:
        if sessions_played < params['sessions']:
            # Random initialization of bookmaker client
            client_no = random.randint(1, 2)
            bets_number = get_rand_sessions(sessions_played)
            print 'MAIN:', bets_number, 'Bets will be placed'
            if client_no == 1:
                client = TonyBet('phantom', params['bet_size'], bets_number,
                                 params['login_attempts'], params['odd_1'], params['odd_2'])
            elif client_no == 2:
                client = TopSport('phantom', params['bet_size'], bets_number,
                                  params['login_attempts'], params['odd_1'], params['odd_2'])

            # Future clients
                '''
            elif client_no == 3:
                client = Xbet('chrome', params['allowed_bet_size'], get_rand_sessions(), params['login_attempts'], odd_1, odd_2)
            else:
                client = Orakulas('chrome', params['allowed_bet_size'], get_rand_sessions(), params['login_attempts'], odd_1, odd_2)
                '''

            client.start()
            client.join()
            sessions_played += client.get_bets_placed()

            # Error management section
            print [client.names['client'], client.get_bets_placed(), client.exit_flag]
            if client.exit_flag == -1 or client.exit_flag == -3 or client.exit_flag == -4:
                break
            if client.exit_flag == -2:
                if connection_errors < params['connection_errors']:
                    connection_errors += 1
                    print 'MAIN: Waiting for internet'
                    time.sleep(120)
                else:
                    print 'MAIN: Severe connection issues'
                    break
            if client.exit_flag == 0 and client.get_bets_placed() != bets_number:
                if unusual_errors < params['unusual_errors']:
                    print 'MAIN: Unusual behavior'
                else:
                    print 'MAIN: Severe unusual behavior'
                    break

        # Sleep during the play
        sleep_time = sleeper(sleep_time, sessions_played)
        odd_switch()

        # Check if new day & reset local variables
        if is_new_day(start_date):
            start_date = datetime.datetime.today().date()
            sessions_played = 0
            unusual_errors = 0
            connection_errors = 0
            sleep_time = params['sleep_time']


def get_rand_sessions(sessions_played):
    lower_limit = 4
    upper_limit = params['sessions'] - sessions_played
    if lower_limit < upper_limit:
        if upper_limit > 16:
            return random.randint(lower_limit, 16)
    return upper_limit


def sleeper(sleep_time, sessions_played):
    if sessions_played < params['sessions']:
        sleep_sec = random.randint(0, sleep_time)
        print 'MAIN: Gonna sleep (in seconds) -', str(sleep_sec)
        time.sleep(sleep_sec)
        return sleep_time - sleep_sec
    else:
        t = datetime.datetime.today()
        future = datetime.datetime(t.year, t.month, t.day, 0, 0)
        future += datetime.timedelta(days=1)
        sleep_sec = (future - t).seconds + 10
        print 'MAIN: Gonna sleep till new day (in seconds) -', str(sleep_sec)
        time.sleep(sleep_sec)
        return 0


def is_new_day(old_date):
    new_date = datetime.datetime.today().date()
    if old_date != new_date:
        return True
    else:
        return False


def instructions():
    print('Choose:\n'
          '1) Show parameters\n'
          '2) Reset sessions per day\n'
          '3) Reset sleep time per day\n'
          '4) Reset bet size\n'
          '5) Reset max login attempts\n'
          '6) Reset max allowed connection errors\n'
          '7) Launch auto better\n'
          '8) Switch odd numbers\n'
          '0) End program\n')


def print_parameters():
    print 'Sessions per day (as int): ' + str(params['sessions']) +\
          '\nSleep time per day in seconds (as int): ' + str(params['sleep_time']) + \
          '\nBet size (as str): ' + params['bet_size'] +\
          '\nMax login attempts (as int): ' + str(params['login_attempts']) +\
          '\nMax allowed connection errors (as int): ' + str(params['connection_errors']) +\
          '\nMax unusual errors allowed (as int): ' + str(params['unusual_errors']) +\
          '\nFirst odd code (as str): ' + params['odd_1']['number'] + ' - ' + params['odd_1']['name'] +\
          '\nSecond odd code (as str): ' + params['odd_2']['number'] + ' - ' + params['odd_2']['name'] +\
          '\nOdd ratio (as str): ' + params['odd_1']['odd'] + '\n'


def get_number(message):
    try:
        return int(input(message))
    except NameError:
        print 'Numeric values accepted only'
        return get_number(message)
    except SyntaxError:
        print 'Numeric values accepted only'
        return get_number(message)


# Global setters
def odd_switch():
    global params
    tmp = params['odd_1']
    params['odd_1'] = params['odd_2']
    params['odd_2'] = tmp


def set_sessions_per_day():
    global params
    params['sessions'] = get_number('Enter sessions per day (min 1): ')
    while params['sessions'] < 1:
        print 'Value entered is to small'
        params['sessions'] = get_number('Enter sessions per day (min 1): ')


def set_sleep_seconds():
    global params
    params['sleep_time'] = get_number('Enter sleep seconds per session (min 0): ')
    while params['sleep_time'] <= 0 or params['sleep_time'] > 86400:
        print 'Value interval [0, 86400)'
        params['sleep_time'] = get_number('Enter sleep seconds per session (min 0): ')


def set_bet_size():
    global params
    size = get_number('Enter bet size (min 50): ')
    while size < 50:
        print 'Value entered is to small'
        size = get_number('Enter bet size (min 50): ')
    params['bet_size'] = str(size)


def set_login_attempts():
    global params
    params['login_attempts'] = get_number('Enter max login attempts per session(min 1): ')
    while params['login_attempts'] < 1:
        print 'Value entered is to small'
        set_login_attempts()


def set_max_connection_errors():
    global params
    params['connection_errors'] = get_number('Enter max connection errors per day(min 1): ')
    while params['connection_errors'] < 1:
        print 'Value entered is to small'
        set_max_connection_errors()


def read_params():
    with open('param.txt', 'r') as my_file:
        return my_file.readline()
    

def write_params():
    with open('param.txt', 'w') as my_file:
        my_file.write(str(params))


def set_params(data_str):
    global params
    params = ast.literal_eval(data_str.strip())


if __name__ == '__main__':
    print 'This is auto better bot, that bets in sites TonyBet & TopSport (V4.3)'
    set_params(read_params())
    instructions()
    choice = 1

    while choice:
        if choice == 1:
            print_parameters()
        if choice == 2:
            set_sessions_per_day()
            print 'Sessions per day changed\n'
            write_params()
        if choice == 3:
            set_sleep_seconds()
            print 'Sleep seconds per day changed\n'
            write_params()
        if choice == 4:
            set_bet_size()
            print 'Bet size changed\n'
            write_params()
        if choice == 5:
            set_login_attempts()
            print 'Max login attempts changed\n'
            write_params()
        if choice == 6:
            set_max_connection_errors()
            print 'Max allowed connection errors changed\n'
            write_params()
        if choice == 7:
            play()
        if choice == 8:
            odd_switch()
            print 'Odd codes switched\n'
            write_params()
        if choice > 8 or choice < 0:
            print 'Bad choice\n'
            instructions()
        choice = get_number('Enter choice: ')

    print 'Program end'

