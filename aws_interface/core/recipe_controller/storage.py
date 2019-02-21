from .base import RecipeController


class StorageRecipeController(RecipeController):
    RECIPE = 'storage'

    def __init__(self):
        super(StorageRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('create_folder', 'cloud.storage.create_folder')
        self.put_cloud_api('upload_file', 'cloud.storage.upload_file')
        self.put_cloud_api('delete_path', 'cloud.storage.delete_path')
        self.put_cloud_api('download_file', 'cloud.storage.download_file')
