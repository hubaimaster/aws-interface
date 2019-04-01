from .base import ServiceController
from .utils import lambda_method, make_data


class StorageServiceController(ServiceController):
    RECIPE = 'storage'

    def __init__(self, resource, app_id):
        super(StorageServiceController, self).__init__(resource, app_id)

    @lambda_method
    def create_folder(self, recipe, parent_path, folder_name, read_groups, write_groups):
        import cloud.storage.create_folder as method
        params = {
            'parent_path': parent_path,
            'folder_name': folder_name,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def upload_file(self, recipe, parent_path, file_name, file_bin, read_groups, write_groups):
        import cloud.storage.upload_file as method
        params = {
            'parent_path': parent_path,
            'file_name': file_name,
            'file_bin': file_bin,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def delete_path(self, recipe, path):
        import cloud.storage.delete_file as method
        params = {
            'path': path,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def download_file(self, recipe, file_path):
        import cloud.storage.download_file as method
        params = {
            'file_path': file_path,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)

    @lambda_method
    def get_folder_list(self, recipe, folder_path, start_key):
        import cloud.storage.get_folder_list as method
        params = {
            'folder_path': folder_path,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        return method.do(data, self.resource)
