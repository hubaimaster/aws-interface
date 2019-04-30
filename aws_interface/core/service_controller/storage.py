from .base import ServiceController
from .utils import lambda_method, make_data


class StorageServiceController(ServiceController):
    RECIPE = 'storage'

    def __init__(self, resource, app_id):
        super(StorageServiceController, self).__init__(resource, app_id)

    @lambda_method
    def upload_b64(self, recipe, parent_file_id, file_name, file_b64, read_groups, write_groups):
        import cloud.storage.upload_b64 as method
        params = {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_b64(self, recipe, file_id):
        import cloud.storage.delete_b64 as method
        params = {
            'file_id': file_id,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def download_b64(self, recipe, file_id):
        import cloud.storage.download_b64 as method
        params = {
            'file_id': file_id,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_b64_info_items(self, recipe, start_key):
        import cloud.storage.get_b64_info_items as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

