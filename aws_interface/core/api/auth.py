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

    def set_email_login(self, enabled, default_group_name):
        return self.service_controller.set_email_login(enabled, default_group_name)

    def set_guest_login(self, enabled, default_group_name):
        return self.service_controller.set_guest_login(enabled, default_group_name)

    def get_email_login(self):
        return self.service_controller.get_email_login()

    def get_guest_login(self):
        return self.service_controller.get_guest_login()

    def create_user(self, email, password, extra):
        return self.service_controller.create_user(email, password, extra)

    def set_user(self, user_id, email, password, extra):
        return self.service_controller.set_user(user_id, email, password, extra)

    def delete_user(self, user_id):
        return self.service_controller.delete_user(user_id)

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
