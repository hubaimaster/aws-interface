from .base import ServiceController
from .utils import lambda_method, make_data


class LogicServiceController(ServiceController):
    SERVICE_TYPE = 'logic'

    def __init__(self, resource, app_id):
        super(LogicServiceController, self).__init__(resource, app_id)

    @lambda_method
    def run_function(self, function_name, payload):
        import cloud.logic.run_function as method
        params = {
            'function_name': function_name,
            'payload': payload,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_function(self, function_name, description, runtime, handler, zip_file, runnable):
        import cloud.logic.create_function as method
        params = {
            'function_name': function_name,
            'description': description,
            'runtime': runtime,
            'handler': handler,
            'zip_file': zip_file,
            'runnable': runnable,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_function(self, function_name):
        import cloud.logic.delete_function as method
        params = {
            'function_name': function_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_function(self, function_name):
        import cloud.logic.get_function as method
        params = {
            'function_name': function_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_functions(self):
        import cloud.logic.get_functions as method
        params = {}
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_function_test(self, test_name, function_name, test_input):
        import cloud.logic.create_function_test as method
        params = {
            'test_name': test_name,
            'function_name': function_name,
            'test_input': test_input,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_function_tests(self):
        import cloud.logic.get_function_tests as method
        params = {}
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_function_test(self, test_name):
        import cloud.logic.delete_function_test as method
        params = {
            'test_name': test_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
