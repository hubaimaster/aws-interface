from core.recipe_controller import DatabaseRecipeController
from core.service_controller import DatabaseServiceController
from .base import API


class DatabaseAPI(API):
    RC_CLASS = DatabaseRecipeController
    SC_CLASS = DatabaseServiceController

    # Recipe
    def get_partitions(self):
        return self.recipe_controller.get_partitions()

    def put_partition(self, partition_name):
        return self.recipe_controller.put_partition(partition_name)

    def delete_partition(self, partition_name):
        return self.recipe_controller.delete_partition(partition_name)

    # Service
    def create_item(self, partition, item, read_permissions=['all'], write_permissions=['all']):
        return self.service_controller.create_item(self.recipe_controller.to_json(),
                                                   partition, item, read_permissions, write_permissions)

    def update_item(self, item_id, item, read_permissions=['all'], write_permissions=['all']):
        return self.service_controller.update_item(self.recipe_controller.to_json(),
                                                   item_id, item, read_permissions, write_permissions)

    def put_item_field(self, item_id, field_name, field_value):
        return self.service_controller.put_item_field(self.recipe_controller.to_json(),
                                                      item_id, field_name, field_value)

    def get_item(self, item_id):
        return self.service_controller.get_item(self.recipe_controller.to_json(), item_id)

    def delete_item(self, item_id):
        return self.service_controller.delete_item(self.recipe_controller.to_json(), item_id)

    def get_items(self, partition, reverse=True, start_key=None):  # New item will be on the top
        return self.service_controller.get_items(self.recipe_controller.to_json(), partition, reverse, start_key)

    def get_item_count(self, partition):
        return self.service_controller.get_item_count(self.recipe_controller.to_json(), partition)

    def search_items(self, query):
        raise NotImplementedError()
