from .base import API
from .utils import lambda_method, make_data


class StorageAPI(API):
    @lambda_method
    def upload_b64(self, parent_file_id, file_name, file_b64):
        import cloud.storage.upload_b64 as method
        params = {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_b64(self, file_id):
        import cloud.storage.delete_b64 as method
        params = {
            'file_id': file_id,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def download_b64(self, file_id):
        import cloud.storage.download_b64 as method
        params = {
            'file_id': file_id,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_b64_info_items(self, start_key, reverse):
        import cloud.storage.get_b64_info_items as method
        params = {
            'start_key': start_key,
            'reverse': reverse,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_policy_code(self, mode):
        import cloud.storage.get_policy_code as method
        params = {
            'mode': mode,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def put_policy(self, mode, code):
        import cloud.storage.put_policy as method
        params = {
            'mode': mode,
            'code': code,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
