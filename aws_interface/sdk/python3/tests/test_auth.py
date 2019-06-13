"""
When the class of this code is initialized, it is registered.
When each test function is executed, login is executed by setUp function.
When each test function is finished, tearDown function is executed and logout is performed.

* If you run the test code after downloading the SDK,
the execution base path will change,
so you must use the import code that in the comments. [from aws_interface import Client]
"""
import unittest
from ..aws_interface import Client
# from aws_interface import Client


class TestAuth(unittest.TestCase):
    client = None
    user_email = 'test@email.com'
    user_password = 'password1234'

    @classmethod
    def setUpClass(cls):
        """
        SDK Register
        :return: None
        """
        cls.client = Client()
        cls.client.auth_register(cls.user_email, cls.user_password)

    def setUp(self):
        """
        This method is called when a function with prefix [test_] is called.
        SDK Login
        :return:
        """
        self.client.auth_login(self.user_email, self.user_password)

    def tearDown(self):
        """
        This method is called when a function with prefix [test_] is ended.
        :return:
        """
        self.client.auth_logout()

    def test_auth_get_me(self):
        """
        Get and compare emails recorded on the server to see if the function works well.
        The register is already called by the setUp function so is not called by this function.
        :return:
        """
        resp = self.client.auth_get_me()
        self.assertTrue(resp['item']['email'] == self.user_email)
