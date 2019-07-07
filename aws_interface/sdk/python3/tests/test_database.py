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


class TestDatabase(unittest.TestCase):
    client = None
    user_email = 'ttest@gmail.com'
    user_password = 'ttestpassword'
    partition = 'test-partition'
    item = {'type': 'test'}
    read_groups = ["user", "admin"]
    write_groups = ["user", "admin"]
    field_name = 'test-field'
    field_value = 'test-field-value'
    read_groups_new = ["user"]
    write_groups_new = ["user"]
    query = [{"option": "or", "field": "read_groups", "condition": "in", "value": "user"}]

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
        Create a item in a database
        :return: None
        """
        resp = self.client.database_create_item(self.partition, self.item, self.read_groups, self.write_groups)
        self.item_id = resp['item_id']

    def tearDown(self):
        """
        This method is called when a function with prefix [test_] is ended.
        Delete created item
        :return: None
        """
        self.client.database_delete_item(self.item_id)

    @classmethod
    def tearDownClass(cls):
        """
        This method is called after all the methods with [test_] is run.
        SDK Logout
        :return: None
        """
        cls.client.auth_logout()

    def test_database_get_item(self):
        """
        Get the item with its item_id and verify with partition name, read_groups, write_groups
        :return: None
        """
        resp = self.client.database_get_item(self.item_id)
        self.assertTrue(resp['item']['partition'] == self.partition)
        self.assertTrue(set(resp['item']['read_groups']) == set(self.read_groups))
        self.assertTrue(set(resp['item']['write_groups']) == set(self.write_groups))

    '''
    def test_database_get_item_count(self):
        """
        Get the number of items in the partition.
        It should be non-negative integer
        :return: None
        """
        resp = self.client.database_get_item_count(self.partition)
        self.assertIsInstance(resp['item']['count'], int)
        self.assertTrue(resp['item']['count'] >= 0)

    def test_database_get_items(self):
        """
        Get a list of items in the partition
        :return: None
        """
        resp = self.client.database_get_items(self.partition)
        self.assertIsInstance(resp['items'], list)

    def test_database_put_item_field(self):
        """
        Add new field with [field_name] and [field_value] on item with [item_id]
        Verify by checking if [field_name] : [field_value] pair is in the item
        :return: None
        """
        self.client.database_put_item_field(self.item_id, self.field_name, self.field_value)
        resp = self.client.database_get_item(self.item_id)
        fields = resp['item']
        self.assertTrue(self.field_name in fields)

    '''
    def test_database_update_item(self):
        """
        Update item
        Verify by checking read_groups and write_groups
        :return: None
        """
        resp = self.client.database_update_item(self.item_id, self.item, self.read_groups_new, self.write_groups_new)
        resp = self.client.database_get_item(self.item_id)
        self.assertTrue(set(resp['item']['read_groups']) == set(self.read_groups_new))
        self.assertTrue(set(resp['item']['write_groups']) == set(self.write_groups_new))

    '''
    def test_database_query_items(self):
        """
        Query and check if the response is in list
        :return: None
        """
        resp = self.client.database_query_items(self.partition, self.query)
        self.assertIsInstance(resp['items'], list)
'''