from core.recipecontroller import *
from core.servicecontroller import *


class API:  # Abstract class
    def __init__(self, bundle, app_id, recipe_json_string=None):
        self.bundle = bundle
        self.app_id = app_id
        self.recipe_json_string = recipe_json_string

        self.recipe_controller = None
        self.service_controller = None
        self.common_init()  # Set recipe and service_controller

    def apply(self):
        self.service_controller.apply(self.recipe_controller)

    def set_recipe_controller(self, recipe_controller):
        self.recipe_controller = recipe_controller

    def get_recipe_controller(self):
        return self.recipe_controller

    def get_recipe_json_string(self):
        return self.get_recipe_controller().to_json()

    def common_init(self):
        # called when __init__ finished, it should implement on subclass. not on abstract class.
        raise NotImplementedError()


class BillAPI(API):
    def common_init(self):
        self.service_controller = BillServiceController(self.bundle, self.app_id)
        self.recipe_controller = BillRecipeController()
        if self.recipe_json_string:
            self.recipe_controller.load_json_string(self.recipe_json_string)

    def get_current_cost(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_cost(start, end)

    def get_current_usage_costs(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_usage_costs(start, end)


class AuthAPI(API):
    def common_init(self):
        self.service_controller = AuthServiceController(self.bundle, self.app_id)
        self.recipe_controller = AuthRecipeController()
        if self.recipe_json_string:
            self.recipe_controller.load_json_string(self.recipe_json_string)

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

    # Service
    def create_user(self, email, password, extra):
        raise NotImplementedError()

    def put_user(self, user_id, email, password, extra):
        raise NotImplementedError()

    def delete_user(self, user_id):
        raise NotImplementedError()

    def get_user(self, user_id):
        raise NotImplementedError()

    def search_user_ids(self, query):  # query ex : 'kim' in col('name') and 21 is col('age')
        raise NotImplementedError()

    def get_user_count(self):
        raise NotImplementedError()


class DatabaseAPI(API):
    def common_init(self):
        return

    # Recipe
    def get_tables(self):
        return self.recipe_controller.get_tables()

    def put_table(self, table_name):
        return self.recipe_controller.put_table(table_name)

    def delete_table(self, table_name):
        raise NotImplementedError()

    def get_table(self, table_name):
        return self.recipe_controller.get_table(table_name)

    # Service
    def get_item(self, item_id):
        raise NotImplementedError()

    def search_item_ids(self, query):
        raise NotImplementedError()

    def create_item(self, item_json):
        raise NotImplementedError()

    def delete_item(self, item_id):
        raise NotImplementedError()

