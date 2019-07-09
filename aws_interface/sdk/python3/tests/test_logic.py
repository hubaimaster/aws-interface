"""
When the class of this code is initialized, it is registered.
When each test function is executed, login is executed by setUp function.
When each test function is finished, tearDown function is executed and logout is performed.

* If you run the test code after downloading the SDK,
the execution base path will change,
so you must use the import code that in the comments. [from aws_interface import Client]
"""
import unittest
# from ..aws_interface import Client
from aws_interface import Client


class TestLogic(unittest.TestCase):
    client = None
    user_email = 'ttest@gmail.com'
    user_password = 'ttestpassword'
    test_function = 'test-function'
    test_payload = {"answer" : 10}

    @classmethod
    def setUpClass(cls):
        """
        SDK Register, Login
        :return: None
        """
        cls.client = Client()
        cls.client.auth_register(cls.user_email, cls.user_password)
        cls.client.auth_login(cls.user_email, cls.user_password)

    def setUp(self):
        """
        This method is called when a function with prefix [test_] is called.
        :return: None
        """

    def tearDown(self):
        """
        This method is called when after all the methods with [test_] is run.
        :return: None
        """

    @classmethod
    def tearDownClass(cls):
        """
        This method is called when a function with prefix [test_] is ended.
        :return: None
        """
        cls.client.auth_logout()

    def test_logic_run_function(self):
        """
        Run function in logic with name [test_function], [test_payload]
        :return: None
        """
        resp = self.client.logic_run_function(self.test_function, self.test_payload)
        self.assertTrue(resp['response']['answer'] == 11)