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
    def create_function(self, function_name, description, runtime, handler, sdk_config, zip_file, runnable):
        import cloud.logic.create_function as method
        params = {
            'function_name': function_name,
            'description': description,
            'runtime': runtime,
            'handler': handler,
            'zip_file': zip_file,
            'runnable': runnable,
            'sdk_config': sdk_config,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def update_function(self, function_name, description, runtime, handler, sdk_config, zip_file, runnable):
        import cloud.logic.update_function as method
        params = {
            'function_name': function_name,
            'description': description,
            'runtime': runtime,
            'handler': handler,
            'zip_file': zip_file,
            'runnable': runnable,
            'sdk_config': sdk_config,
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
    def get_function_zip_b64(self, function_name):
        import cloud.logic.get_function_zip_b64 as method
        params = {
            'function_name': function_name,
        }
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

    @lambda_method
    def get_function_file_paths(self, function_name):
        import cloud.logic.get_function_file_paths as method
        params = {
            'function_name': function_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_function_file(self, function_name, file_path):
        import cloud.logic.get_function_file as method
        params = {
            'function_name': function_name,
            'file_path': file_path,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def put_function_file(self, function_name, file_path, function_file, function_type):
        import cloud.logic.put_function_file as method
        params = {
            'function_name': function_name,
            'file_path': file_path,
            'file_content': function_file,
            'file_type': function_type,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_webhook(self, name, description, function_name):
        import cloud.logic.create_webhook as method
        params = {
            'name': name,
            'description': description,
            'function_name': function_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_webhook(self, name):
        import cloud.logic.delete_webhook as method
        params = {
            'name': name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_webhook(self, name):
        import cloud.logic.get_webhook as method
        params = {
            'name': name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_webhook_url(self, name):
        import cloud.logic.get_webhook_url as method
        params = {
            'name': name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_webhooks(self, start_key):
        import cloud.logic.get_webhooks as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
