from core.recipe_controller import AuthRecipeController
from core.service_controller import AuthServiceController
from .base import API


class AuthAPI(API):
    RC_CLASS = AuthRecipeController
    SC_CLASS = AuthServiceController

    # Recipe
    def get_user_groups(self):
        return self.recipe_controller.get_user_groups()

    def put_user_group(self, name, description):
        return self.recipe_controller.put_user_group(name, description)

    def delete_user_group(self, name):
        return self.recipe_controller.delete_user_group(name)

    def set_email_login(self, enabled, default_group_name):
        return self.recipe_controller.set_email_login(enabled, default_group_name)

    def set_guest_login(self, enabled, default_group_name):
        return self.recipe_controller.set_guest_login(enabled, default_group_name)

    def get_email_login(self):
        return self.recipe_controller.get_email_login()

    def get_guest_login(self):
        return self.recipe_controller.get_guest_login()

    # Service
    def create_user(self, email, password, extra):
        return self.service_controller.create_user(self.recipe_controller.to_json(), email, password, extra)

    def set_user(self, user_id, email, password, extra):
        return self.service_controller.set_user(self.recipe_controller.to_json(), user_id, email, password, extra)

    def delete_user(self, user_id):
        return self.service_controller.delete_user(self.recipe_controller.to_json(), user_id)

    def get_user(self, user_id):
        return self.service_controller.get_user(self.recipe_controller.to_json(), user_id)

    def get_users(self, start_key=None, limit=100):
        return self.service_controller.get_users(self.recipe_controller.to_json(), start_key, limit)

    def get_user_count(self):
        return self.service_controller.get_user_count(self.recipe_controller.to_json())

    def create_session(self, email, password):  # use as login
        return self.service_controller.create_session(self.recipe_controller.to_json(), email, password)

    def delete_session(self, session_id):  # use as logout
        return self.service_controller.delete_session(self.recipe_controller.to_json(), session_id)

    def get_session(self, session_id):  # use as login check
        return self.service_controller.get_session(self.recipe_controller.to_json(), session_id)

    def get_sessions(self, start_key=None, limit=100):  # it will connect for dashboard (use as list logged in users)
        return self.service_controller.get_sessions(self.recipe_controller.to_json(), start_key, limit)

    def get_session_count(self):  # it will connect for dashboard
        return self.service_controller.get_session_count(self.recipe_controller.to_json())
