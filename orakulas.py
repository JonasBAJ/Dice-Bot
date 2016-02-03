from webDriver import SeleniumDrive, Keys
from threading import Thread
import random
import time

__author__ = 'Jonas Bajorinas'


# This module was not tested in real life
class _OrakulasParameters:
    def __init__(self):
        self.fields = {
            'login': '#user_login_username',
            'password': '#user_login_password',
        }
        self.buttons = {
            'login': '#header > header > div > div.menu-wrapper > div.top-menu > ul > li.has-submenu.item-login',
            'logout_1': '#header > header > div > div.menu-wrapper > div.top-menu > ul > li.has-submenu.item-profile',
            'logout_2': '#header > header > div > div.menu-wrapper > div.top-menu > ul > li.has-submenu.item-profile '
                        '> ul > li.last > a',
        }
        self.other = {
            'login_status': '#header > header > div > div.menu-wrapper > div.top-menu > ul > '
                            'li.has-submenu.item-profile > div > span',
            'iframe': '#betgames_iframe_1'
        }
        self.names = {
            'client': 'ORAKULAS: ',
            'user': 'user_email',                           # TODO: Enter user name
            'password': 'user_password',                    # TODO: Enter user password
            'check_name': 'check_name'                      # TODO: Enter check fraze which can be founded in web site
        }
        self.urls = {
            'host': 'http://orakulas.lt/',
            'timer': 'http://orakulas.betgames.tv/ext/game/ping/orakulas/4',
            'bet': 'http://orakulas.betgames.tv/ext/client/accept_bet_ajax/orakulas/',
            'neutral': 'http://orakulas.lt/games/bet-games'
        }


class Orakulas(Thread, SeleniumDrive, _OrakulasParameters):

    # Constructor & destructor
    def __init__(self, drive_name='', bet_size='', bets_allowed=0, max_login_times=0, odd_1=0, odd_2=0):
        _OrakulasParameters.__init__(self)
        SeleniumDrive.__init__(self, self.names['client'], drive_name)
        Thread.__init__(self)
        # Public fields
        self.exit_flag = 0
        # Private fields
        self.__bets_placed = 0
        self.__bets_allowed = bets_allowed
        self.__login_times = 0
        self.__login_allowed = max_login_times
        self.__bet_url_1 = self.__set_bet_url(odd_1, bet_size)
        self.__bet_url_2 = self.__set_bet_url(odd_2, bet_size)

    def __destructor(self):
        self.driver.quit()

    # Private methods
    def __login(self):
        if self.go_to(self.urls['host']):
            time.sleep(0.5)
            self.button_click(self.buttons['login'])
            login_field = self.find_by_css(self.fields['login'])
            password_field = self.find_by_css(self.fields['password'])
            if login_field != -1 or password_field != -1:
                login_field.clear()
                login_field.send_keys(self.names['user'])
                time.sleep(0.5)
                password_field.send_keys(self.names['password'])
                password_field.send_keys(Keys.ENTER)
                my_name = self.find_by_css(self.other['login_status'])
                if str(my_name.text).lower() == self.names['check_name'].lower():
                    return 1
                else:
                    self.event_logger('Login status not confirmed')
                    return -3
            self.event_logger('Login field not found')
            return -1
        else:
            self.event_logger('Connection error')
            return -2                                               # Connection lost signal

    def __logout(self):
        if self.go_to(self.urls['host']):
            if self.button_click(self.buttons['logout']):
                return 1
            else:
                return -1
        return -2                                                   # Connection lost signal

    def __place_bet(self, time_wait, bet_url):
        wait = random.randint(1, int(time_wait*0.3))
        print self.names['client'] + 'Estimated wait time ' + str(wait)
        time.sleep(wait)
        if self.go_to(self.urls['neutral']):
            if self.go_to(bet_url):
                if self.get_json_value('body > pre', 'success'):
                    self.go_to(self.urls['neutral'])
                    return 1
                else:
                    return -1
        return -2

    def __get_timer(self):
        if self.go_to(self.urls['timer']):
            time.sleep(0.5)
            resp = self.get_json_value('body', 'seconds_left')
            if resp > 0:
                return int(resp)
            else:
                return 0
        else:
            return -2

    def __inc_bets_placed(self):
        self.__bets_placed += 1

    def __inc_login_times(self):
        self.__login_times += 1

    def __set_bet_url(self, odd, bet_size):
        if odd and bet_size:
            path = odd['number'] + '/' + odd['odd'] + '/' + bet_size + '/?'
            url = self.urls['bet'] + path
            print self.names['client'] + odd['name']
            return url
        else:
            return False

    # Public methods
    def run(self):
        login = False
        if not self.__bet_url_1 and not self.__bet_url_2:           # Check if bet url's are given
            print self.names['client'] + 'Bet URL\'s not set'
            self.exit_flag = -1                                     # Bet url not set
        else:
            while True:
                if not login:                                       # Check login
                    self.__inc_login_times()
                    if self.__login_times > self.__login_allowed:
                        self.event_logger('Max login attempts exceeded')
                        self.exit_flag = -4                         # Login attempts exceeded
                        break
                    response = self.__login()
                    if response == 1:
                        print self.names['client'] + 'Login successful'
                        login = True
                    elif response == -1:
                        print self.names['client'] + 'Trying to login again'
                        resp = self.__logout()
                        if resp == -2:                              # Says that client is already logged out
                            self.exit_flag = -2                     # Connection error
                            break
                        else:                                       # If -1 or 1 continue -> login
                            continue
                    else:
                        self.exit_flag = response                   # Connection error
                        break

                timer = self.__get_timer()                          # Check timer
                if timer == -2:
                    self.exit_flag = -2
                    break
                elif timer < 30:
                    print self.names['client'] + 'Waiting for new session'
                    time.sleep(20)
                    continue

                resp_1 = self.__place_bet(timer, self.__bet_url_1)
                resp_2 = self.__place_bet(timer, self.__bet_url_2)

                if resp_1 == 1 and resp_2 == 1:
                    self.__inc_bets_placed()
                    print self.names['client'] + str(self.__bets_placed) + ' Bets successful'
                    time.sleep(self.__get_timer() + 10)
                    if self.__bets_placed == self.__bets_allowed:    # Break if max bets reached
                        break
                elif resp_1 == -2 or resp_2 == -2:
                    self.exit_flag = -2                              # Connection error
                    break
                elif resp_1 == -1 or resp_2 == -1:
                    login = False
                    continue

        # End of session
        self.__destructor()

    def get_bets_placed(self):
        return self.__bets_placed

    def __get_info(self, date_str):
        source_list = list()
        if self.__login() == 1:
            # Navigate
            self.button_click(self.buttons['live_lottery'])
            self.button_click(self.buttons['bet_history'])
            self.driver.switch_to.frame(self.find_by_css(self.other['iframe']))
            # Det data
            if self.enter_data(self.fields['date'], date_str, 0.5):
                if self.button_click(self.buttons['filter']):
                    source_list.append(self.get_source_txt(self.driver.page_source))
                    i = 2
                    while True:
                        page_css = 'body > div.container > div:nth-child(6) > div > ul > li:nth-child('+str(i)+') > a'
                        if self.button_click(page_css):
                            source_list.append(self.get_source_txt(self.driver.page_source))
                            i += 1
                        else:
                            break
                    self.__destructor()
                    return source_list
        else:
            self.__destructor()
            return source_list


