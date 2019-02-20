from django.apps import AppConfig
from .models import Recipe, App


def reset_background_apply():
    """
    If the server was interrupted while a Recipe was getting
    initialized, indicate that the initialization has failed.
    :return:
    """
    Recipe.objects.all().filter(apply_status=Recipe.INIT_PROGRESS).update(apply_status=Recipe.INIT_FAILED)
    App.objects.all().update(applying_in_background=False)


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        reset_background_apply()

