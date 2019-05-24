from core.service_controller import LogicServiceController
from .base import API


class LogicAPI(API):
    SC_CLASS = LogicServiceController

    # Service
    def create_function(self, function_name, description, runtime, handler, zip_file=None, runnable=True):
        return self.service_controller.create_function(function_name, description, runtime, handler, zip_file, runnable)

    def delete_function(self, function_name):
        return self.service_controller.delete_function(function_name)

    def update_function(self, function_name, description, zip_file=None, run_groups=[]):
        return self.service_controller.update_function(function_name, description, zip_file, run_groups)

    def get_functions(self):
        return self.service_controller.get_functions()

    def get_function(self, function_name):
        return self.service_controller.get_function(function_name)

    def run_function(self, function_name, payload):
        return self.service_controller.run_function(function_name, payload)

    def create_function_test(self, test_name, function_name, test_input):
        return self.service_controller.create_function_test(test_name, function_name, test_input)

    def get_function_tests(self):
        return self.service_controller.get_function_tests()

    def delete_function_test(self, test_name):
        return self.service_controller.delete_function_test(test_name)
