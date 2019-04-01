from .base import ServiceController
from .utils import lambda_method, make_data


class AuthServiceController(ServiceController):
    RECIPE = 'auth'

    def __init__(self, resource, app_id):
        super(AuthServiceController, self).__init__(resource, app_id)

    @lambda_method
    def create_user(self, recipe, email, password, extra):
        import cloud.auth.register as method
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def set_user(self, recipe, user_id, email, password, extra):
        import cloud.auth.set_user as method
        parmas = {
            'user_id': user_id,
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_user(self, recipe, user_id):
        import cloud.auth.delete_user as method
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_user(self, recipe, user_id):
        import cloud.auth.get_user as method
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_user_count(self, recipe):
        import cloud.auth.get_user_count as method
        parmas = {

        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_users(self, recipe, start_key, limit):
        import cloud.auth.get_users as method
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def create_session(self, recipe, email, password):
        import cloud.auth.login as method
        params = {
            'email': email,
            'password': password
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_session(self, recipe, session_id):
        import cloud.auth.logout as method
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_sessions(self, recipe, session_ids):
        import cloud.auth.delete_sessions as method
        params = {
            'session_ids': session_ids
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_session(self, recipe, session_id):
        import cloud.auth.get_session as method
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_sessions(self, recipe, start_key, limit):
        import cloud.auth.get_sessions as method
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_session_count(self, recipe):
        import cloud.auth.get_session_count as method
        parmas = {}
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def create_admin(self, recipe, email, password, extra):
        import cloud.auth.register_admin as method
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        return method.do(data, self.resource)
