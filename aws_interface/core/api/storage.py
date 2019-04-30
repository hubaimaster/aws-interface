from core.recipe_controller import StorageRecipeController
from core.service_controller import StorageServiceController
from .base import API


class StorageAPI(API):
    RC_CLASS = StorageRecipeController
    SC_CLASS = StorageServiceController

    # Recipe

    # Service

    def upload_b64(self, parent_file_id, file_name, file_b64, read_groups, write_groups):
        return self.service_controller.upload_b64(self.recipe_controller.to_json_string(),
                                                  parent_file_id, file_name, file_b64, read_groups, write_groups)

    def delete_b64(self, file_key):
        return self.service_controller.delete_b64(self.recipe_controller.to_json_string(), file_key)

    def download_b64(self, file_id):
        return self.service_controller.download_b64(self.recipe_controller.to_json_string(), file_id)

    def get_b64_info_items(self, start_key):
        return self.service_controller.get_b64_info_items(self.recipe_controller.to_json_string(), start_key)
