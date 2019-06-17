from core.service_controller import AuthServiceController
from .base import API


class AuthAPI(API):
    SC_CLASS = AuthServiceController

    def get_user_groups(self):
        return self.service_controller.get_user_groups()

    def put_user_group(self, name, description):
        return self.service_controller.put_user_group(name, description)

    def delete_user_group(self, name):
        return self.service_controller.delete_user_group(name)

    def set_login_method(self, login_method, enabled, default_group_name, register_policy_code):
        return self.service_controller.set_login_method(login_method, enabled, default_group_name, register_policy_code)

    def get_login_method(self, login_method):
        return self.service_controller.get_login_method(login_method)

    def create_user(self, email, password, extra):
        return self.service_controller.create_user(email, password, extra)

    def set_user(self, user_id, field, value):
        return self.service_controller.set_user(user_id, field, value)

    def delete_user(self, user_id):
        return self.service_controller.delete_user(user_id)

    def delete_users(self, user_ids):
        return self.service_controller.delete_users(user_ids)

    def get_user(self, user_id):
        return self.service_controller.get_user(user_id)

    def get_users(self, start_key=None, limit=100):
        return self.service_controller.get_users(start_key, limit)

    def get_user_count(self):
        return self.service_controller.get_user_count()

    def create_session(self, email, password):  # use as login
        return self.service_controller.create_session(email, password)

    def delete_session(self, session_id):  # use as logout
        return self.service_controller.delete_session(session_id)

    def delete_sessions(self, session_ids):  # use as logout
        return self.service_controller.delete_sessions(session_ids)

    def get_session(self, session_id):  # use as login check
        return self.service_controller.get_session(session_id)

    def get_sessions(self, start_key=None, limit=100):  # it will connect for dashboard (use as list logged in users)
        return self.service_controller.get_sessions(start_key, limit)

    def get_session_count(self):  # it will connect for dashboard
        return self.service_controller.get_session_count()

    def create_admin(self, email, password, extra):
        return self.service_controller.create_admin(email, password, extra)

    def attach_group_permission(self, group_name, permission):
        return self.service_controller.attach_group_permission(group_name, permission)

    def detach_group_permission(self, group_name, permission):
        return self.service_controller.detach_group_permission(group_name, permission)

    def attach_user_group(self, user_id, group_name):
        return self.service_controller.attach_user_group(user_id, group_name)

    def detach_user_group(self, user_id, group_name):
        return self.service_controller.detach_user_group(user_id, group_name)

    def set_me(self, field, value):
        return self.service_controller.set_me(field, value)

    def get_all_permissions(self):
        return self.service_controller.get_all_permissions()
