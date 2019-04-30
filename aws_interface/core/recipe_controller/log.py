from .base import RecipeController


class LogRecipeController(RecipeController):
    RECIPE = 'log'

    def _init_cloud_api(self):
        self.put_cloud_api('create_log', 'cloud.log.create_log')
        return
