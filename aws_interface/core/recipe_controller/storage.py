from .base import RecipeController


class StorageRecipeController(RecipeController):
    RECIPE = 'storage'

    def __init__(self):
        super(StorageRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('upload_b64', 'cloud.storage.upload_b64')
        self.put_cloud_api('delete_b64', 'cloud.storage.delete_b64')
        self.put_cloud_api('download_b64', 'cloud.storage.download_b64')
