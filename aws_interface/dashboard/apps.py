from django.apps import AppConfig
from .models import Recipe


def reset_recipe_initialization():
    """
    If the server was interrupted while a Recipe was getting
    initialized, indicate that the initialization has failed.
    :return:
    """
    Recipe.objects.all().filter(init_status=Recipe.INIT_PROGRESS).update(init_status=Recipe.INIT_FAILED)


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        reset_recipe_initialization()

