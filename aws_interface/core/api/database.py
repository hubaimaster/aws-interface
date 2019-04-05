from core.recipe_controller import DatabaseRecipeController
from core.service_controller import DatabaseServiceController
from .base import API


class DatabaseAPI(API):
    RC_CLASS = DatabaseRecipeController
    SC_CLASS = DatabaseServiceController

    # Service
    def create_item(self, partition, item, read_groups=['admin'], write_groups=['admin']):
        return self.service_controller.create_item(self.recipe_controller.to_json(),
                                                   partition, item, read_groups, write_groups)

    def update_item(self, item_id, item, read_groups=['admin'], write_groups=['admin']):
        return self.service_controller.update_item(self.recipe_controller.to_json(),
                                                   item_id, item, read_groups, write_groups)

    def put_item_field(self, item_id, field_name, field_value):
        return self.service_controller.put_item_field(self.recipe_controller.to_json(),
                                                      item_id, field_name, field_value)

    def get_item(self, item_id):
        return self.service_controller.get_item(self.recipe_controller.to_json(), item_id)

    def delete_item(self, item_id):
        return self.service_controller.delete_item(self.recipe_controller.to_json(), item_id)

    def delete_items(self, item_ids):
        return self.service_controller.delete_items(self.recipe_controller.to_json(), item_ids)

    def get_items(self, partition, reverse=True, start_key=None):  # New item will be on the top
        return self.service_controller.get_items(self.recipe_controller.to_json(), partition, reverse, start_key)

    def get_item_count(self, partition):
        return self.service_controller.get_item_count(self.recipe_controller.to_json(), partition)

    def create_partition(self, partition):
        return self.service_controller.create_partition(self.recipe_controller.to_json(), partition)

    def delete_partition(self, partition):
        return self.service_controller.delete_partition(self.recipe_controller.to_json(), partition)

    def delete_partitions(self, partitions):
        return self.service_controller.delete_partitions(self.recipe_controller.to_json(), partitions)

    def get_partitions(self):
        return self.service_controller.get_partitions(self.recipe_controller.to_json())

    def query_items(self, partition, query, start_key=None):
        return self.service_controller.query_items(self.recipe_controller.to_json(), partition, query, start_key)
