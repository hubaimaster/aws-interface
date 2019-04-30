from core.recipe_controller import LogicRecipeController
from core.service_controller import LogicServiceController
from .base import API


class LogicAPI(API):
    RC_CLASS = LogicRecipeController
    SC_CLASS = LogicServiceController

    # Service
    def create_function(self, function_name, description, zip_file=None, run_groups=['user']):
        return self.service_controller.create_function(self.recipe_controller.to_json_string(),
                                                       function_name, description, zip_file, run_groups)

    def delete_function(self, function_name):
        return self.service_controller.delete_function(self.recipe_controller.to_json_string(),
                                                       function_name)

    def update_function(self, function_name, description, zip_file=None, run_groups=['user']):
        return self.service_controller.update_function(self.recipe_controller.to_json_string(),
                                                       function_name, description, zip_file, run_groups)

    def get_functions(self):
        return self.service_controller.get_functions(self.recipe_controller.to_json_string())

    def get_function(self, function_name):
        return self.service_controller.get_function(self.recipe_controller.to_json_string(), function_name)

    def run_function(self, function_name, payload):
        return self.service_controller.run_function(self.recipe_controller.to_json_string(), function_name, payload)
