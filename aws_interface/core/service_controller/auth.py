from .base import ServiceController
from .utils import lambda_method, make_data
from cloud.aws import *


class AuthServiceController(ServiceController):
    RECIPE = 'auth'

    def __init__(self, bundle, app_id):
        super(AuthServiceController, self).__init__(bundle, app_id)
        self._init_table()

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'auth-' + self.app_id
        dynamodb.init_table(table_name)
        dynamodb.update_table(table_name, indexes=[{
            'hash_key': 'partition',
            'hash_key_type': 'S',
            'sort_key': 'email',
            'sort_key_type': 'S',
        }])
        return

    @lambda_method
    def create_user(self, recipe, email, password, extra):
        import cloud.auth.register as register
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return register.do(data, boto3)['body']

    @lambda_method
    def set_user(self, recipe, user_id, email, password, extra):
        import cloud.auth.set_user as set_user
        parmas = {
            'user_id': user_id,
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return set_user.do(data, boto3)

    @lambda_method
    def delete_user(self, recipe, user_id):
        import cloud.auth.delete_user as delete_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return delete_user.do(data, boto3)

    @lambda_method
    def get_user(self, recipe, user_id):
        import cloud.auth.get_user as get_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user.do(data, boto3)

    @lambda_method
    def get_user_count(self, recipe):
        import cloud.auth.get_user_count as get_user_count
        parmas = {

        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user_count.do(data, boto3)

    @lambda_method
    def get_users(self, recipe, start_key, limit):
        import cloud.auth.get_users as get_users
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_users.do(data, boto3)

    @lambda_method
    def create_session(self, recipe, email, password):
        import cloud.auth.login as login
        params = {
            'email': email,
            'password': password
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return login.do(data, boto3)

    @lambda_method
    def delete_session(self, recipe, session_id):
        import cloud.auth.logout as logout
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return logout.do(data, boto3)

    @lambda_method
    def get_session(self, recipe, session_id):
        import cloud.auth.get_session as get_session
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_session.do(data, boto3)

    @lambda_method
    def get_sessions(self, recipe, start_key, limit):
        import cloud.auth.get_sessions as get_sessions
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_sessions.do(data, boto3)

    @lambda_method
    def get_session_count(self, recipe):
        import cloud.auth.get_session_count as get_session_count
        parmas = {}
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_session_count.do(data, boto3)
