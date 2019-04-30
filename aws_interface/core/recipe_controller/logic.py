from .base import RecipeController


class LogicRecipeController(RecipeController):
    RECIPE = 'logic'

    def __init__(self):
        super(LogicRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('run_function', 'cloud.logic.run_function')
