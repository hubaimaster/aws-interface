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


class TestAuth(unittest.TestCase):
    client = None
    user_email = 'ttest@gmail.com'
    user_password = 'ttestpassword'
    user_id = 'jK5iK6UgYnTdaRhow5yvAT'
    fb_access_token = ''

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
        :return: None
        """
        self.client.auth_login(self.user_email, self.user_password)

    def tearDown(self):
        """
        This method is called when a function with prefix [test_] is ended.
        :return: None
        """
        self.client.auth_logout()

    def test_auth_get_me(self):
        """
        Get and compare emails recorded on the server to see if the function works well.
        The register is already called by the setUp function so is not called by this function.
        :return: None
        """
        resp = self.client.auth_get_me()
        self.assertTrue(resp['item']['email'] == self.user_email)

    def test_auth_get_user(self):
        """
        Get a user with its id and compare the email to verify.
        :return: None
        """
        user_id = self.client.auth_get_me()['item']['id']
        resp = self.client.auth_get_user(user_id)
        self.assertTrue(resp['item']['email'] == self.user_email)

    def test_auth_get_users(self):
        """
        Get a list of users with page [start_key]
        :return: None
        """
        resp = self.client.auth_get_users()
        self.assertIsInstance(resp['items'], list)

    def test_auth_login_facebook(self):
        """
        Log in with facebook.
        Check 'session id' in response to verify
        Since it is already logged in in setup method, need to log out first.
        :return: None
        """
        self.client.auth_logout()
        resp = self.client.auth_login_facebook(self.fb_access_token)
        self.assertIsNotNone(resp['session_id'])

    def test_auth_guest(self):
        """
        Log in as guest.
        Check 'session id' in response to verify
        Since it is already logged in in setup method, need to log out first.
        :return: None
        """
        self.client.auth_logout()
        resp = self.client.auth_guest()
        self.assertIsNotNone(resp['session_id'])

