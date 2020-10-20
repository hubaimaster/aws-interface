from .base import API
from .utils import lambda_method, make_data


class TriggerAPI(API):
    @lambda_method
    def delete_trigger(self, trigger_id):
        import cloud.trigger.delete_trigger as method
        params = {
            'trigger_id': trigger_id,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_triggers(self, start_key, limit, reverse):
        import cloud.trigger.get_triggers as method
        params = {
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_trigger(self, trigger_name, module_name, function_name):
        import cloud.trigger.create_trigger as method
        params = {
            'trigger_name': trigger_name,
            'module_name': module_name,
            'function_name': function_name
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
