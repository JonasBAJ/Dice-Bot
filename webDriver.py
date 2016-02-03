from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import datetime
import logging
import string
import unicodedata

__author__ = 'Jonas Bajorinas'


class SeleniumDrive:

    # Constructor & destructor
    def __init__(self, name, drive_name=''):
        if drive_name == 'chrome':
            opts = Options()
            opts.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " \
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29." \
                              "0.1547.57 Safari/537.36")
            self.driver = webdriver.Chrome()
        else:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " \
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29." \
                         "0.1547.57 Safari/537.36"
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = user_agent
            self.driver = webdriver.PhantomJS(desired_capabilities=dcap)

        self.__client_name = name
        self.driver.set_page_load_timeout(30)
        self.driver.maximize_window()
        logging.basicConfig(filename='exeption.log',)

    # Public methods
    def button_click(self, css_path):
        button = self.find_by_css(css_path)
        if button != -1:
            try:
                self.driver.execute_script('return arguments[0].scrollIntoView(true);', button)
                actions = ActionChains(self.driver)
                actions.move_to_element(button)
                actions.click(button)
                actions.perform()
                time.sleep(1)
                return True
            except WebDriverException:
                button.send_keys(Keys.PAGE_UP)
                actions = ActionChains(self.driver)
                actions.move_to_element(button)
                actions.click(button)
                actions.perform()
                time.sleep(1)
                return True
        else:
            return False

    def enter_data(self, css_path, str_data, wait_time):
        value_field = self.find_by_css(css_path)
        if value_field != -1:
            try:
                self.driver.execute_script('return arguments[0].scrollIntoView(true);', value_field)
                value_field.send_keys(Keys.ESCAPE)
                time.sleep(wait_time)
                value_field.clear()
                time.sleep(wait_time)
                value_field.send_keys(str_data)
                return True
            except WebDriverException:
                value_field.send_keys(Keys.PAGE_UP)
                value_field.send_keys(Keys.ESCAPE)
                time.sleep(wait_time)
                value_field.clear()
                time.sleep(wait_time)
                value_field.send_keys(str_data)
                return True
        else:
            return False

    def get_balance(self, css_balance):
        balance_uni = self.driver.find_element_by_css_selector(css_balance).text
        balance_str = unicodedata.normalize('NFKD', balance_uni).encode('ascii', 'ignore')
        balance_int = int(balance_str.translate(string.maketrans('', ''), string.punctuation))
        return balance_int

    def go_to(self, url):
        try:
            self.driver.get(url)
            return True
        except WebDriverException:
            time.sleep(3)
            try:
                self.driver.get(url)
                return True
            except WebDriverException, e:
                self.event_logger(str(e))
                return False

    def find_by_css(self, css):
        try:
            elem = self.driver.find_element_by_css_selector(css)
            return elem
        except NoSuchElementException:
            time.sleep(2)
            try:
                elem = self.driver.find_element_by_css_selector(css)
                return elem
            except NoSuchElementException:
                self.driver.refresh()
                time.sleep(2)
                try:
                    elem = self.driver.find_element_by_css_selector(css)
                    return elem
                except NoSuchElementException, e:
                    self.event_logger(str(e))
                    return -1

    def get_json_value(self, css_path, index):
        json_txt = self.find_by_css(css_path)
        if json_txt != -1:
            json_list = json.loads(json_txt.text)
            return json_list[index]
        else:
            return False

    @staticmethod
    def get_source_txt(source):
        text = unicodedata.normalize('NFKD', source).encode('ascii', 'ignore')
        return text

    def event_logger(self, message):
        event_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')              # Get timestamp
        with open('exeption.log', 'a') as my_file:
            init_message = '\n' + event_date + ' ' + self.__client_name                 # Compose message
            my_file.write(init_message)
        logging.exception(message)                                                      # Write message to log file

    def bet_logger(self, message):
        event_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')              # Get timestamp
        with open('bet.log', 'a') as my_file:
            init_message = '\n' + event_date + ' ' + self.__client_name + message       # Compose message
            my_file.write(init_message)

    def check_timer(self, css_path):
        try:
            time_left_str = str(self.driver.find_element_by_css_selector(css_path).text)
            time_left = time.strptime(time_left_str, '%M:%S')
            time_in_sec = datetime.timedelta(minutes=time_left.tm_min, seconds=time_left.tm_sec).total_seconds()
            return time_in_sec
        except ValueError, e:
            self.event_logger(str(e))
            return 0


