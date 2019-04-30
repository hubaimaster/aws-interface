from .base import Adapter
from dashboard.models import App, Recipe
from core.recipe_controller import rc_dict
import simplejson as json


class DjangoAdapter(Adapter):
    def __init__(self, app_id, request):
        self.app = App.objects.get(id=app_id)
        self.credential = request.session.get('credentials', {})

    def _get_app_id(self):
        return self.app.id

    def _get_credential(self):
        return self.credential

    def _get_vendor(self):
        return self.app.vendor

    def _load_recipe_json_string(self, recipe_type):
        recipe, created = Recipe.objects.get_or_create(app=self.app, name=recipe_type)
        return recipe.json_string

    def _save_recipe_json_string(self, recipe_type, json_string):
        recipe, created = Recipe.objects.get_or_create(app=self.app, name=recipe_type)
        recipe.json_string = json_string
        recipe.save()

