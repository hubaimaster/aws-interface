from .base import API
from .utils import lambda_method, make_data


class ScheduleAPI(API):
    @lambda_method
    def create_schedule(self, schedule_name, schedule_expression, function_name, payload):
        import cloud.schedule.create_schedule as method
        params = {
            'schedule_name': schedule_name,
            'schedule_expression': schedule_expression,
            'function_name': function_name,
            'payload': payload
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_schedule(self, schedule_name):
        import cloud.schedule.delete_schedule as method
        params = {
            'schedule_name': schedule_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_schedule(self, schedule_name):
        import cloud.schedule.get_schedule as method
        params = {
            'schedule_name': schedule_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_schedules(self, start_key=None):
        import cloud.schedule.get_schedules as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
