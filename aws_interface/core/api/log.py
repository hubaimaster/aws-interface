from core.recipe_controller import LogRecipeController
from core.service_controller import LogServiceController
from .base import API


class LogAPI(API):
    RC_CLASS = LogRecipeController
    SC_CLASS = LogServiceController

    # Service
    def create_log(self, event_source, event_name, event_param):
        return self.service_controller.create_log(self.recipe_controller.to_json_string(),
                                                  event_source, event_name, event_param)

    def get_logs(self, event_source=None, event_name=None, event_param=None, user_id=None):
        return self.service_controller.delete_function(self.recipe_controller.to_json_string(),
                                                       event_source, event_name, event_param, user_id)
