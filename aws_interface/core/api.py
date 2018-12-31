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
        return error, result

    def create_user_group(self, group_name):
        rc = AuthRecipeController(self.boto3_session)
        error, result = rc.create_user_group(group_name)
        return error, result

    #Service controller
    def create_user(self, email, password, extra):
        sc = AuthServiceController(self.boto3_session)
        error, result = sc.create_user(email, password, extra)
        return error, result