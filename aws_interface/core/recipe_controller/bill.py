from .base import RecipeController


class BillRecipeController(RecipeController):
    RECIPE = 'bill'

    def _init_cloud_api(self):
        return
