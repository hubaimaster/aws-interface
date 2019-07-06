"""
When the class of this code is initialized, it is registered.
When each test function is executed, login is executed by setUp function.
When each test function is finished, tearDown function is executed and logout is performed.

* If you run the test code after downloading the SDK,
the execution base path will change,
so you must use the import code that in the comments. [from aws_interface import Client]
"""
import unittest
import os
# from ..aws_interface import Client
from aws_interface import Client


class TestStorage(unittest.TestCase):
    client = None
    user_email = 'ttest@gmail.com'
    user_password = 'ttestpassword'
    file_path = os.path.abspath(os.path.join(os.curdir, 'test.txt'))
    download_path = os.path.abspath(os.path.join(os.curdir, 'test_download.txt'))
    read_groups = ["user", "admin"]
    write_groups = ["user", "admin"]

    @classmethod
    def setUpClass(cls):
        """
        SDK Register, Login
        Create text file to upload
        :return: None
        """
        cls.client = Client()
        cls.client.auth_register(cls.user_email, cls.user_password)
        cls.client.auth_login(cls.user_email, cls.user_password)
        with open(cls.file_path, 'w') as tp:
            tp.write("this is a test text")

    def setUp(self):
        """
        This method is called when a function with prefix [test_] is called.
        Upload a file
        :return: None
        """
        resp = self.client.storage_upload_file(self.file_path, self.read_groups, self.write_groups)
        self.file_id = resp['file_id']

    def tearDown(self):
        """
        This method is called when a function with prefix [test_] is ended.
        Delete file from storage
        :return: None
        """
        self.client.storage_delete_file(self.file_id)

    @classmethod
    def tearDownClass(cls):
        """
        This method is called after all the methods with [test_] is run.
        SDK Logout
        Remove test file from local
        :return: None
        """
        cls.client.auth_logout()
        os.remove(cls.file_path)

    def test_storage_download_file(self):
        """
        Download a file and compare it with original file
        :return: None
        """
        self.client.storage_download_file(self.file_id, self.download_path)
        with open(self.file_path, 'r') as of:
            with open(self.download_path, 'r') as wf:
                self.assertTrue(of.read() == wf.read())