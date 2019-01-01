import json
from core.layer1 import *


class API:
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session


class AuthAPI(API):
    #Recipe controller
    def get_user_groups(self):
        rc = AuthRecipeController(self.boto3_session)
        error, result = rc.get_user_groups()
        return NotImplementedError()  #{ 'error' : str, 'message' : str, 'body': json}

    def create_user_group(self, group_name):
        rc = AuthRecipeController(self.boto3_session)
        error, result = rc.create_user_group(group_name)
        return NotImplementedError()

    def delete_user_group(self, group_name):
        return NotImplementedError()

    #Service controller
    def create_user(self, email, password, extra):
        sc = AuthServiceController(self.boto3_session)
        error, result = sc.create_user(email, password, extra)
        return NotImplementedError()

    def put_user(self, user_id, email, password, extra):
        return NotImplementedError()

    def delete_user(self, user_id):
        return NotImplementedError()

    def get_user(self, user_id):
        return NotImplementedError()

    def search_user_ids(self, query): # query ex : 'kim' in col('name') and 21 is col('age')
        return NotImplementedError()



class DatabaseAPI(API):
    # Recipe controller
    def get_table_ids(self):
        return NotImplementedError()

    def create_table(self, table_name):
        return NotImplementedError()

    def delete_table(self, table_id):
        return NotImplementedError()

    def get_table(self, table_id):
        return NotImplementedError()

    # SC

    def get_item(self, item_id):
        return NotImplementedError()

    def search_item_ids(self, query):
        return NotImplementedError()

    def create_item(self, item_json):
        return NotImplementedError()

    def delete_item(self, item_id):
        return NotImplementedError()

