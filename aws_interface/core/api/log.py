from .base import API
from .utils import lambda_method, make_data


class LogAPI(API):
    @lambda_method
    def create_log(self, event_source, event_name, event_param):
        import cloud.log.create_log as method
        params = {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_logs(self, event_source=None, event_name=None, event_param=None, user_id=None, start_key=None, reverse=False):
        import cloud.log.get_logs as method
        params = {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
            'user_id': user_id,
            'start_key': start_key,
            'reverse': reverse,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
