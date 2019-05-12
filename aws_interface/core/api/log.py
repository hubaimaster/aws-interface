from core.service_controller import LogServiceController
from .base import API


class LogAPI(API):
    SC_CLASS = LogServiceController

    # Service
    def create_log(self, event_source, event_name, event_param):
        return self.service_controller.create_log(event_source, event_name, event_param)

    def get_logs(self, event_source=None, event_name=None, event_param=None, user_id=None):
        return self.service_controller.get_logs(event_source, event_name, event_param, user_id)
