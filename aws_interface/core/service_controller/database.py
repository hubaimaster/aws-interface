from .base import ServiceController
from .utils import lambda_method, make_data

from cloud.aws import *


class DatabaseServiceController(ServiceController):
    RECIPE = 'database'

    def __init__(self, bundle, app_id):
        super(DatabaseServiceController, self).__init__(bundle, app_id)
        self._init_table()

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'database-{}'.format(self.app_id)
        dynamodb.init_table(table_name)
        return

    def common_apply(self, recipe_controller):
        return

    @lambda_method
    def create_item(self, recipe, partition, item, read_groups, write_groups):
        import cloud.database.create_item as method
        params = {
            'partition': partition,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def update_item(self, recipe, item_id, item, read_groups, write_groups):
        import cloud.database.update_item as method
        params = {
            'item_id': item_id,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def put_item_field(self, recipe, item_id, field_name, field_value):
        import cloud.database.put_item_field as method
        params = {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def get_item(self, recipe, item_id):
        import cloud.database.get_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def delete_item(self, recipe, item_id):
        import cloud.database.delete_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def get_items(self, recipe, partition, reverse, start_key):
        import cloud.database.get_items as method
        params = {
            'partition': partition,
            'reverse': reverse,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def get_item_count(self, recipe, partition):
        import cloud.database.get_item_count as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)
