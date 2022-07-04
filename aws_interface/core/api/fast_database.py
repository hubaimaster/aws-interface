from .base import API
from .utils import make_data, lambda_method


class FastDatabaseAPI(API):
    @lambda_method
    def create_item(self, partition, item, can_overwrite=False):
        import cloud.fast_database.create_item as method
        params = {
            'partition': partition,
            'item': item,
            'can_overwrite': can_overwrite
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_items(self, partition, items, can_overwrite=False):
        import cloud.fast_database.create_items as method
        params = {
            'partition': partition,
            'items': items,
            'can_overwrite': can_overwrite,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def update_item(self, partition, item_id, item):
        import cloud.fast_database.update_item as method
        params = {
            'partition': partition,
            'item_id': item_id,
            'item': item,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def update_items(self, partition, item_id_pairs):
        import cloud.fast_database.update_items as method
        params = {
            'partition': partition,
            'item_id_pairs': item_id_pairs
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_item(self, item_id, consistent_read=False):
        import cloud.fast_database.get_item as method
        params = {
            'item_id': item_id,
            'consistent_read': consistent_read
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_items(self, item_ids, consistent_read=False):  # New item will be on the top
        import cloud.fast_database.get_items as method
        params = {
            'item_ids': item_ids,
            'consistent_read': consistent_read
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_item(self, item_id):
        import cloud.fast_database.delete_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_items(self, item_ids):
        import cloud.fast_database.delete_items as method
        params = {
            'item_ids': item_ids,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_partition(self, partition, pk_group, pk_field, sk_group, sk_field, post_sk_fields, use_random_sk_postfix):
        import cloud.fast_database.create_partition as method
        params = {
            'partition': partition,
            'pk_group': pk_group,
            'pk_field': pk_field,

            'sk_group': sk_group,
            'sk_field': sk_field,
            'post_sk_fields': post_sk_fields,
            'use_random_sk_postfix': use_random_sk_postfix,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_partition(self, partition):
        import cloud.fast_database.delete_partition as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_partitions(self):
        import cloud.fast_database.get_partitions as method
        params = {
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def query_items(self, pk_group, pk_field, pk_value,
                    sort_condition=None, sk_group=None, partition=None, sk_field=None, sk_value=None,
                    sk_second_value=None,
                    filters=None, start_key=None, limit=100, reverse=False,
                    consistent_read=False, projection_keys=None, index_name=None):
        """:query:list"""
        import cloud.fast_database.query_items as method
        params = {
            'pk_group': pk_group,
            'pk_field': pk_field,
            'pk_value': pk_value,

            'sort_condition': sort_condition,
            'sk_group': sk_group,
            'partition': partition,
            'sk_field': sk_field,
            'sk_value': sk_value,
            'sk_second_value': sk_second_value,

            'filters': filters,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,

            'consistent_read': consistent_read,
            'projection_keys': projection_keys,
            'index_name': index_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_policy_code(self, partition, mode):
        import cloud.fast_database.get_policy_code as method
        params = {
            'partition': partition,
            'mode': mode,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def put_policy(self, partition, mode, code):
        import cloud.fast_database.put_policy as method
        params = {
            'partition': partition,
            'mode': mode,
            'code': code,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
