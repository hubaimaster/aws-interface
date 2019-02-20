from .base import RecipeController


class DatabaseRecipeController(RecipeController):
    RECIPE = 'database'

    def __init__(self):
        super(DatabaseRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('create_item', 'cloud.database.create_item')
        self.put_cloud_api('delete_item', 'cloud.database.delete_item')
        self.put_cloud_api('get_item', 'cloud.database.get_item')
        self.put_cloud_api('get_items', 'cloud.database.get_items')
        self.put_cloud_api('put_item_field', 'cloud.database.put_item_field')
        self.put_cloud_api('update_item', 'cloud.database.update_item')
        self.put_cloud_api('get_item_count', 'cloud.database.get_item_count')

    def put_partition(self, partition_name):
        if 'partitions' not in self.data:
            self.data['partitions'] = {}
        self.data['partitions'][partition_name] = {
            'name': partition_name
        }

    def get_partitions(self):
        partitions = self.data.get('partitions', {})
        return partitions

    def get_partition(self, partition_name):
        partitions = self.get_partitions()
        partition = partitions.get(partition_name, None)
        return partition

    def delete_partition(self, partition_name):
        if 'partitions' not in self.data:
            self.data['partitions'] = {}
        self.data['partitions'].pop(partition_name)
        return True
