from core.service_controller import LogicServiceController
from .base import API


class LogicAPI(API):
    SC_CLASS = LogicServiceController

    # Service
    def create_function(self, function_name, description, runtime, handler, sdk_config, zip_file=None, runnable=True):
        return self.service_controller.create_function(function_name, description, runtime, handler, sdk_config, zip_file, runnable)

    def delete_function(self, function_name):
        return self.service_controller.delete_function(function_name)

    def update_function(self, function_name, description, runtime=None, handler=None, sdk_config=None, zip_file=None, runnable=None):
        return self.service_controller.update_function(function_name, description, runtime, handler, sdk_config, zip_file, runnable)

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

    def get_function_zip_b64(self, function_name):
        return self.service_controller.get_function_zip_b64(function_name)

    def delete_function_test(self, test_name):
        return self.service_controller.delete_function_test(test_name)

    def get_function_file(self, function_name, file_path):
        return self.service_controller.get_function_file(function_name, file_path)

    def get_function_file_paths(self, function_name):
        return self.service_controller.get_function_file_paths(function_name)

    def put_function_file(self, function_name, file_path, file_content, file_type):
        return self.service_controller.put_function_file(function_name, file_path, file_content, file_type)

    def create_webhook(self, name, description, function_name):
        return self.service_controller.create_webhook(name, description, function_name)

    def delete_webhook(self, name):
        return self.service_controller.delete_webhook(name)

    def get_webhook(self, name):
        return self.service_controller.get_webhook(name)

    def get_webhook_url(self, name):
        return self.service_controller.get_webhook_url(name)

    def get_webhooks(self, start_key=None):
        return self.service_controller.get_webhooks(start_key)
