from .base import ServiceController
from .utils import lambda_method, make_data

from cloud.aws import *


class StorageServiceController(ServiceController):
    RECIPE = 'storage'

    def __init__(self, bundle, app_id):
        super(StorageServiceController, self).__init__(bundle, app_id)
        self._init_bucket()
        self._init_table()

    def _init_bucket(self):
        s3 = S3(self.boto3_session)
        bucket_name = 'storage-{}'.format(self.app_id)
        s3.init_bucket(bucket_name)

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'storage-{}'.format(self.app_id)
        dynamodb.init_table(table_name)

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
        boto3 = self.boto3_session
        return method.do(data, boto3)

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
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def delete_path(self, recipe, path):
        import cloud.storage.delete_path as method
        params = {
            'path': path,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def download_file(self, recipe, file_path):
        import cloud.storage.download_file as method
        params = {
            'file_path': file_path,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @lambda_method
    def get_folder_list(self, recipe, folder_path, start_key):
        import cloud.storage.get_folder_list as method
        params = {
            'folder_path': folder_path,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)
