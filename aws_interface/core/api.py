import json
from core.recipe import *
from core.service_constructor import *

class API:
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session
        self.common_init()

    def common_init(self):
        raise NotImplementedError()

    def apply(self):
        raise NotImplementedError()


class AuthAPI(API):
    def common_init(self):
        return

    #Recipe
    def get_user_groups(self):
        user_groups = self.recipe.get_user_groups()
        return user_groups

    def put_user_group(self, group_name):
        return self.recipe.put_user_group(group_name)

    def delete_user_group(self, group_name):
        raise NotImplementedError()

    #SC
    def create_user(self, email, password, extra):
        raise NotImplementedError()

    def put_user(self, user_id, email, password, extra):
        raise NotImplementedError()

    def delete_user(self, user_id):
        raise NotImplementedError()

    def get_user(self, user_id):
        raise NotImplementedError()

    def search_user_ids(self, query): # query ex : 'kim' in col('name') and 21 is col('age')
        raise NotImplementedError()


class DatabaseAPI(API):
    def common_init(self):
        self.service_constructor()
        return
    # Recipe
    def get_tables(self):
        tables = self.recipe.get_tables()
        raise tables

    def put_table(self, table_name):
        self.recipe.put_table(table_name)
        self.
        return

    def delete_table(self, table_name):
        raise NotImplementedError()

    def get_table(self, table_name):
        table = self.recipe.get_table(table_name)
        return table

    # SC
    def get_item(self, item_id):
        raise NotImplementedError()

    def search_item_ids(self, query):
        raise NotImplementedError()

    def create_item(self, item_json):
        raise NotImplementedError()

    def delete_item(self, item_id):
        raise NotImplementedError()

