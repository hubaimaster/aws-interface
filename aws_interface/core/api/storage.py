from core.service_controller import StorageServiceController
from .base import API


class StorageAPI(API):
    SC_CLASS = StorageServiceController

    # Service

    def upload_b64(self, parent_file_id, file_name, file_b64, read_groups, write_groups):
        return self.service_controller.upload_b64(parent_file_id, file_name, file_b64, read_groups, write_groups)

    def delete_b64(self, file_key):
        return self.service_controller.delete_b64(file_key)

    def download_b64(self, file_id):
        return self.service_controller.download_b64(file_id)

    def get_b64_info_items(self, start_key):
        return self.service_controller.get_b64_info_items(start_key)
