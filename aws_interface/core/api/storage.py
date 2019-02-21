from core.recipe_controller import StorageRecipeController
from core.service_controller import StorageServiceController
from .base import API


class StorageAPI(API):
    RC_CLASS = StorageRecipeController
    SC_CLASS = StorageServiceController

    # Recipe

    # Service
    def create_folder(self, parent_path, folder_name, read_groups, write_groups):
        return self.service_controller.create_folder(self.recipe_controller.to_json(),
                                                     parent_path, folder_name, read_groups, write_groups)

    def upload_file(self, parent_path, file_name, file_bin, read_groups, write_groups):
        return self.service_controller.upload_file(self.recipe_controller.to_json(),
                                                   parent_path, file_name, file_bin, read_groups, write_groups)

    def delete_path(self, path):
        return self.service_controller.delete_path(self.recipe_controller.to_json(), path)

    def get_folder_list(self, folder_path, start_key):
        return self.service_controller.get_folder_list(self.recipe_controller.to_json(), folder_path, start_key)

    def download_file(self, file_path):
        return self.service_controller.download_file(self.recipe_controller.to_json(), file_path)
