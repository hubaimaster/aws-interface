from core.service_controller import LogicServiceController
from .base import API


class LogicAPI(API):
    SC_CLASS = LogicServiceController

    # Service
    def create_function(self, function_name, description, zip_file=None, run_groups=list()):
        return self.service_controller.create_function(function_name, description, zip_file, run_groups)

    def delete_function(self, function_name):
        return self.service_controller.delete_function(function_name)

    def update_function(self, function_name, description, zip_file=None, run_groups=list()):
        return self.service_controller.update_function(function_name, description, zip_file, run_groups)

    def get_functions(self):
        return self.service_controller.get_functions()

    def get_function(self, function_name):
        return self.service_controller.get_function(function_name)

    def run_function(self, function_name, payload):
        return self.service_controller.run_function(function_name, payload)
