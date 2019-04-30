from .base import ServiceController
from .utils import lambda_method, make_data


class LogServiceController(ServiceController):
    RECIPE = 'log'

    def __init__(self, resource, app_id):
        super(LogServiceController, self).__init__(resource, app_id)

    @lambda_method
    def create_log(self, recipe, event_source, event_name, event_param):
        import cloud.log.create_log as method
        params = {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_logs(self, recipe, event_source=None, event_name=None, event_param=None, user_id=None):
        import cloud.log.get_logs as method
        params = {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
            'user_id': user_id,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)