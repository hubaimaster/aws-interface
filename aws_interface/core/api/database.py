from core.service_controller import DatabaseServiceController
from .base import API


class DatabaseAPI(API):
    SC_CLASS = DatabaseServiceController

    # Service
    def create_item(self, partition, item, read_groups, write_groups):
        return self.service_controller.create_item(partition, item, read_groups, write_groups)

    def update_item(self, item_id, item, read_groups, write_groups):
        return self.service_controller.update_item(item_id, item, read_groups, write_groups)

    def put_item_field(self, item_id, field_name, field_value):
        return self.service_controller.put_item_field(item_id, field_name, field_value)

    def get_item(self, item_id):
        return self.service_controller.get_item(item_id)

    def delete_item(self, item_id):
        return self.service_controller.delete_item(item_id)

    def delete_items(self, item_ids):
        return self.service_controller.delete_items(item_ids)

    def get_items(self, partition, reverse=True, start_key=None):  # New item will be on the top
        return self.service_controller.get_items(partition, reverse, start_key)

    def get_item_count(self, partition):
        return self.service_controller.get_item_count(partition)

    def create_partition(self, partition):
        return self.service_controller.create_partition(partition)

    def delete_partition(self, partition):
        return self.service_controller.delete_partition(partition)

    def delete_partitions(self, partitions):
        return self.service_controller.delete_partitions(partitions)

    def get_partitions(self):
        return self.service_controller.get_partitions()

    def query_items(self, partition, query, start_key=None):
        return self.service_controller.query_items(partition, query, start_key)

    def get_policy_code(self, partition_to_apply, mode):
        return self.service_controller.get_policy_code(partition_to_apply, mode)

    def put_policy(self, partition_to_apply, mode, code):
        return self.service_controller.put_policy(partition_to_apply, mode, code)
