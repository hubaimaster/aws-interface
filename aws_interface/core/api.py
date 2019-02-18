from core.recipecontroller import *
from core.servicecontroller import *
from core.util import *
from abc import ABCMeta, abstractmethod
from core import sdk


class API(metaclass=ABCMeta):  # Abstract class
    """
    Make sure to set RC_CLASS and SC_CLASS when you inherit this class.
    """
    RC_CLASS = None
    SC_CLASS = None

    def __init__(self, bundle, app_id, recipe_json_string=None):
        """
        :param bundle:
        :param app_id:
        :param recipe_json_string:
        """
        self.bundle = bundle
        self.app_id = app_id
        self.recipe_json_string = recipe_json_string

        self.recipe_controller = type(self).RC_CLASS(bundle, app_id)
        self.service_controller = type(self).SC_CLASS()

        if self.recipe_json_string:
            self.recipe_controller.load_json_string(self.recipe_json_string)

    def apply(self):
        self.service_controller.apply(self.recipe_controller)

    def set_recipe_controller(self, recipe_controller):
        self.recipe_controller = recipe_controller

    def get_recipe_controller(self):
        return self.recipe_controller

    def get_recipe_json_string(self):
        return self.get_recipe_controller().to_json()

    def get_rest_api_url(self):
        return self.service_controller.get_rest_api_url(self.recipe_controller)


class BillAPI(API):
    RC_CLASS = BillRecipeController
    SC_CLASS = BillServiceController

    def get_current_cost(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_cost(start, end)

    def get_current_usage_costs(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_usage_costs(start, end)


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


class DatabaseAPI(API):
    RC_CLASS = DatabaseRecipeController
    SC_CLASS = DatabaseServiceController

    # Recipe
    def get_partitions(self):
        return self.recipe_controller.get_partitions()

    def put_partition(self, partition_name):
        return self.recipe_controller.put_partition(partition_name)

    def delete_partition(self, partition_name):
        return self.recipe_controller.delete_partition(partition_name)

    # Service
    def create_item(self, partition, item, read_permissions=['all'], write_permissions=['all']):
        return self.service_controller.create_item(self.recipe_controller.to_json(),
                                                   partition, item, read_permissions, write_permissions)

    def update_item(self, item_id, item, read_permissions=['all'], write_permissions=['all']):
        return self.service_controller.update_item(self.recipe_controller.to_json(),
                                                   item_id, item, read_permissions, write_permissions)

    def put_item_field(self, item_id, field_name, field_value):
        return self.service_controller.put_item_field(self.recipe_controller.to_json(),
                                                      item_id, field_name, field_value)

    def get_item(self, item_id):
        return self.service_controller.get_item(self.recipe_controller.to_json(), item_id)

    def delete_item(self, item_id):
        return self.service_controller.delete_item(self.recipe_controller.to_json(), item_id)

    def get_items(self, partition, reverse=True):  # New item will be on the top
        return self.service_controller.get_items(self.recipe_controller.to_json(), partition, reverse)

    def get_item_count(self, partition):
        return self.service_controller.get_item_count(self.recipe_controller.to_json(), partition)

    def search_items(self, query):
        raise NotImplementedError()


class StorageAPI(API):
    def __init__(self, bundle, app_id, recipe_json_string=None):
        super(StorageAPI, self).__init__(bundle, app_id, recipe_json_string)
        self.service_controller = StorageServiceController(self.bundle, self.app_id)
        self.recipe_controller = StorageRecipeController()
        if self.recipe_json_string:
            self.recipe_controller.load_json_string(self.recipe_json_string)

    # Recipe

    # Service
    def create_folder(self, parent_path, folder_name, read_groups, write_groups):
        return self.service_controller.create_folder(self.recipe_controller.to_json(),
                                                     parent_path, folder_name, read_groups, write_groups)

    def upload_file(self, parent_path, file_name, file_bin, read_groups, write_groups):
        return self.service_controller.upload_file(self.recipe_controller.to_json(),
                                                   parent_path, file_name, file_bin, read_groups, write_groups)

    def delete_folder(self, folder_path):
        return self.service_controller.delete_folder(self.recipe_controller.to_json(), folder_path)

    def delete_file(self, file_path):
        return self.service_controller.delete_file(self.recipe_controller.to_json(), file_path)

    def get_folder_list(self, folder_path, start_key):
        return self.service_controller.get_folder_list(self.recipe_controller.to_json(), folder_path, start_key)

    def download_file(self, file_path):
        return self.service_controller.download_file(self.recipe_controller.to_json(), file_path)


def generate_sdk(apis, platform):
    controller_pairs = []
    api: API
    for api in apis:
        rc = api.get_recipe_controller()
        sc = api.service_controller
        controller_pairs.append((rc, sc))
    return sdk.generate(controller_pairs, platform)


api_list = [
    BillAPI, AuthAPI, DatabaseAPI, StorageAPI
]
