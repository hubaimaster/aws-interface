"""Django live server test code
Dashboard login and register,
Auth, Bill, Database, Storage, Log, Logic,
Download SDK and run test
"""
import time
import platform
import tempfile
import shutil
import os
import json
import settings
from urllib.request import urlopen
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import select
from botocore.exceptions import ClientError


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(settings.__file__)))
SECRET_DIR = os.path.join(BASE_DIR, 'secret')
SECRET_BASE_DIR = os.path.join(SECRET_DIR, 'base.json')

try:
    SECRETS_BASE = json.load(open(SECRET_BASE_DIR, 'rt'))
    ACCESS_KEY = SECRETS_BASE['AWS_ACCESS_KEY']
    SECRET_KEY = SECRETS_BASE['AWS_SECRET_KEY']
except Exception:
    raise BaseException('Could not find secret file {}'.format(SECRET_BASE_DIR))


TEST_STRING = 'testapp'
APP_NAME = '{}'.format(TEST_STRING)

DELAY = 2
LONG_DELAY = 4
WEB_DRIVE_LINUX = 'https://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_linux64.zip'
WEB_DRIVE_MAC = 'https://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_mac64.zip'
WEB_DRIVE_WINDOWS = 'https://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_win32.zip'

LOGIN_URL = '/login'
APPS_URL = '/apps'

EMAIL = 'test@{}.com'.format(TEST_STRING)
PASSWORD = 'TEST_PASSWORD'


class DashboardTestCase(StaticLiveServerTestCase):
    def setUp(self):
        """
        Download web drivers and
        register aws-i and login and
        create aws-i application
        :return:
        """
        self.download_dir = tempfile.mkdtemp()
        self.drive_path = self._download_web_drive()
        self.browser = webdriver.Chrome(chrome_options=self.get_options(), executable_path=self.drive_path)
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)
        self._set_register()
        self._set_login()
        self._create_app()
        print("Delay for allocating resources")
        time.sleep(LONG_DELAY * 10)
        self.is_init = True

    def get_options(self):
        """
        Get options for download functions in web driver
        Setting about downloaded file's dir and other options
        :return: options:Options
        """
        options = Options()
        options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        return options

    def _download_web_drive(self):
        """
        Download each OS version of web drivers from google's web site
        And return Path of downloaded web driver's zip file
        :return: path
        """
        name = 'chromedriver'
        self.temp_dir = tempfile.mkdtemp()
        temp = tempfile.mktemp(suffix='.zip', dir=self.temp_dir)
        system = platform.system()
        if system == 'Linux':
            url = WEB_DRIVE_LINUX
        elif system == 'Darwin':
            url = WEB_DRIVE_MAC
        elif system == 'Windows':
            url = WEB_DRIVE_WINDOWS
            name += '.exe'
        with urlopen(url) as res:
            res_data = res.read()
            with open(temp, 'wb+') as f:
                f.write(res_data)
            shutil.unpack_archive(temp, self.temp_dir)
        path = os.path.join(self.temp_dir, name)
        os.chmod(path, 0o777)
        return path

    def _set_register(self):
        self.browser.find_element_by_id('register').click()
        time.sleep(DELAY)
        self.browser.find_element_by_id('email').send_keys(EMAIL)
        self.browser.find_element_by_id('password').send_keys(PASSWORD)
        self.browser.find_element_by_id('password-check').send_keys(PASSWORD)
        time.sleep(DELAY)
        self.browser.find_element_by_id('access_key').send_keys(ACCESS_KEY)
        self.browser.find_element_by_id('secret_key').send_keys(SECRET_KEY)
        time.sleep(DELAY)
        self.browser.find_element_by_id('register').click()
        time.sleep(DELAY)
        alert_text = self.browser.switch_to.alert.text
        print('alert_text:{}'.format(alert_text))
        self.browser.switch_to.alert.accept()
        if len(alert_text) < 1:
            self.assertFalse()

    def _create_app(self):
        self.browser.get(self.live_server_url + APPS_URL)
        time.sleep(DELAY)
        self.browser.find_element_by_id('create-new-project').click()
        time.sleep(DELAY)
        self.browser.find_element_by_id('input-username').send_keys(APP_NAME)
        self.browser.find_element_by_id('create-app').click()
        time.sleep(DELAY)
        self.browser.switch_to.alert.accept()
        time.sleep(DELAY)
        self.browser.find_element_by_id('app-{}'.format(APP_NAME)).click()
        self.assertEqual(self.browser.current_url.endswith('overview'), True)
        while True:
            time.sleep(DELAY)
            overlay_count = len(self.browser.find_elements_by_class_name('loadingoverlay'))
            if overlay_count == 0:
                break
        time.sleep(LONG_DELAY * 6)

    def _is_alert_presented(self):
        try:
            print(self.browser.switch_to.alert)
            return True
        except NoAlertPresentException as ex:
            print(ex)
            return False

    def get_view_tag(self):
        try:
            view_tag = self.browser.find_element_by_id('view-tag').get_attribute('value')
        except NoSuchElementException as ex:
            print(ex)
            return None
        return view_tag

    def assert_view_tag(self, view_tag):
        self.assertEqual(self.get_view_tag(), view_tag)

    def tearDown(self):
        time.sleep(DELAY)
        self.browser.get(self.live_server_url + APPS_URL)
        time.sleep(DELAY)
        self.browser.find_element_by_id('setting-{}'.format(APP_NAME)).click()
        time.sleep(DELAY)
        self.browser.find_element_by_id('delete-{}'.format(APP_NAME)).click()
        time.sleep(20)
        self.browser.quit()
        shutil.rmtree(self.temp_dir)

    def _remove_temp(self):
        shutil.rmtree(self.download_dir)

    def _set_login(self):
        self.browser.get(self.live_server_url + LOGIN_URL)
        time.sleep(DELAY)
        self.browser.find_element_by_id('email').send_keys(EMAIL)
        self.browser.find_element_by_id('password').send_keys(PASSWORD)
        self.browser.find_element_by_id('login').click()
        time.sleep(DELAY)
        self.assertEqual(APPS_URL in self.browser.current_url, True)

    def wait_overlay(self):
        while self.browser.find_elements_by_class_name('loadingoverlay'):
            time.sleep(LONG_DELAY)
            print("waiting for page loading")
        print("Page loaded")

    def do_test_process(self):
        from dashboard.tests.auth import AuthTestProcess
        from dashboard.tests.bill import BillTestProcess
        from dashboard.tests.database import DatabaseTestProcess
        from dashboard.tests.storage import StorageTestProcess
        from dashboard.tests.logic import LogicTestProcess
        from dashboard.tests.sdk import SDKTestProcess
        AuthTestProcess(self).do_test()
        #DatabaseTestProcess(self).do_test()
        #StorageTestProcess(self).do_test()
        #LogTestProcess(self).do_test
        LogicTestProcess(self).do_test()
        #SDKTestProcess(self).do_test()

    def test(self):
        self.do_test_process()