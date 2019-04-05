from .base import ServiceController
from .utils import lambda_method, make_data


class DatabaseServiceController(ServiceController):
    RECIPE = 'database'

    def __init__(self, resource, app_id):
        super(DatabaseServiceController, self).__init__(resource, app_id)

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
        return method.do(data, self.resource)

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
        return method.do(data, self.resource)

    @lambda_method
    def put_item_field(self, recipe, item_id, field_name, field_value):
        import cloud.database.put_item_field as method
        params = {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_item(self, recipe, item_id):
        import cloud.database.get_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_item(self, recipe, item_id):
        import cloud.database.delete_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_items(self, recipe, item_ids):
        import cloud.database.delete_items as method
        params = {
            'item_ids': item_ids,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_items(self, recipe, partition, reverse, start_key):
        import cloud.database.get_items as method
        params = {
            'partition': partition,
            'reverse': reverse,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_item_count(self, recipe, partition):
        import cloud.database.get_item_count as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def create_partition(self, recipe, partition):
        import cloud.database.create_partition as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_partition(self, recipe, partition):
        import cloud.database.delete_partition as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_partitions(self, recipe, partitions):
        import cloud.database.delete_partitions as method
        params = {
            'partitions': partitions,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_partitions(self, recipe):
        import cloud.database.get_partitions as method
        params = {
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def query_items(self, recipe, partition, query, start_key):
        """:query:list"""
        import cloud.database.query_items as method
        params = {
            'partition': partition,
            'query': query,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)
