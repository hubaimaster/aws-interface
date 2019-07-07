"""
When the class of this code is initialized, it is registered.
When each test function is executed, login is executed by setUp function.
When each test function is finished, tearDown function is executed and logout is performed.

* If you run the test code after downloading the SDK,
the execution base path will change,
so you must use the import code that in the comments. [from aws_interface import Client]
"""
import unittest
import time
# from ..aws_interface import Client
from aws_interface import Client
from bs4 import BeautifulSoup
import requests


class TestLog(unittest.TestCase):
    client = None
    user_email = 'ttest@gmail.com'
    user_password = 'ttestpassword'
    test_event_source = 'test_event_source'
    test_event_name = 'test_event_name'
    test_event_param = None

    @classmethod
    def setUpClass(cls):
        """
        SDK Register, Login
        :return: None
        """
        cls.client = Client()
        cls.client.auth_register(cls.user_email, cls.user_password)
        cls.client.auth_login(cls.user_email, cls.user_password)

    @classmethod
    def tearDownClass(cls):
        """
        This method is called after all the methods with [test_] is run.
        SDK Logout
        :return: None
        """
        cls.client.auth_logout()

    def test_log_create_log(self):
        """
        :return: None
        """
        self.client.log_create_log(self.test_event_source, self.test_event_name, self.test_event_param)