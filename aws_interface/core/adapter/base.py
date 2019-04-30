from abc import ABCMeta
from core.api import *
from core.recipe_controller import rc_list, rc_dict
from resource import get_resource_allocator
from contextlib import contextmanager
import simplejson as json


class Adapter(metaclass=ABCMeta):
    allocation_busy = False

    def _get_app_id(self):
        raise NotImplementedError

    def _get_credential(self):
        raise NotImplementedError

    def _get_vendor(self):
        raise NotImplementedError

    def _load_recipe_json_string(self, recipe_type):
        raise NotImplementedError

    def _save_recipe_json_string(self, recipe_type, json_string):
        raise NotImplementedError

    def _get_recipe_json_string(self, recipe_type):
        print('recipe_type:', recipe_type)
        default_json_string = rc_dict[recipe_type]().to_json_string()
        default_json = json.loads(default_json_string)
        json_object = json.loads(self._load_recipe_json_string(recipe_type))
        for key in json_object:
            default_json[key] = json_object[key]
        return default_json

    @contextmanager
    def open_api_auth(self):
        """
            You can do this:
            with adapter.open_api_auth() as auth:
            use(auth)
        """
        recipe_type = 'auth'
        api = AuthAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
                      self._get_recipe_json_string(recipe_type))
        yield api
        self._save_recipe_json_string(recipe_type, api.get_recipe_json_string())

    @contextmanager
    def open_api_bill(self):
        recipe_type = 'bill'
        api = BillAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
                      self._get_recipe_json_string(recipe_type))
        yield api
        self._save_recipe_json_string(recipe_type, api.get_recipe_json_string())

    @contextmanager
    def open_api_database(self):
        recipe_type = 'database'
        api = DatabaseAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
                          self._get_recipe_json_string(recipe_type))
        yield api
        self._save_recipe_json_string(recipe_type, api.get_recipe_json_string())

    @contextmanager
    def open_api_storage(self):
        recipe_type = 'storage'
        api = StorageAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
                         self._get_recipe_json_string(recipe_type))
        yield api
        self._save_recipe_json_string(recipe_type, api.get_recipe_json_string())

    @contextmanager
    def open_api_logic(self):
        recipe_type = 'logic'
        api = LogicAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
                       self._get_recipe_json_string(recipe_type))
        yield api
        self._save_recipe_json_string(recipe_type, api.get_recipe_json_string())

    # @contextmanager
    # def open_api_log(self):
    #     recipe_type = 'log'
    #     api = LogAPI(self._get_vendor(), self._get_credential(), self._get_app_id(),
    #                   self._load_recipe_json(recipe_type))
    #     yield api
    #     self._save_recipe_json(recipe_type, api.get_recipe_json_string())
    #

    def generate_sdk(self, platform):
        recipes = [self._get_recipe_json_string(recipe_type) for recipe_type in rc_list]
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id(), recipes)
        return allocator.generate_sdk(platform)

    def allocate_resource(self):
        if self.allocation_busy:
            print('Allocation process is busy. Try again after few minutes.')
            return
        self.allocation_busy = True
        recipes = [self._get_recipe_json_string(recipe_type) for recipe_type in rc_list]
        try:
            allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id(), recipes)
            allocator.create()
            self.allocation_busy = False
        except Exception as e:
            print(e)
            self.allocation_busy = False
            return False
        return True

    def get_resource_status(self):  # TODO
        """
        :return: 'allocating-busy' | 'allocating-able' | 'no_resource'
        """

    def terminate_resource(self):
        recipes = [self._get_recipe_json_string(recipe_type) for recipe_type in rc_list]
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id(), recipes)
        allocator.terminate()
