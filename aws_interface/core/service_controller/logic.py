from .base import ServiceController
from .utils import lambda_method, make_data


class LogicServiceController(ServiceController):
    RECIPE = 'logic'

    def __init__(self, resource, app_id):
        super(LogicServiceController, self).__init__(resource, app_id)

    @lambda_method
    def run_function(self, recipe, function_name, payload):
        import cloud.database.create_item as method
        params = {
            'function_name': function_name,
            'payload': payload,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def create_function(self, recipe, function_name, description, zip_file, run_groups):
        return

    @lambda_method
    def delete_function(self, recipe, function_name):
        return

    @lambda_method
    def get_function(self, recipe, function_name):
        return

    @lambda_method
    def get_functions(self, recipe):
        return
