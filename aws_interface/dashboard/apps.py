import sys
from django.apps import AppConfig


def reset_background_apply():
    """
    If the server was interrupted while a Recipe was getting
    initialized, indicate that the initialization has failed.
    :return:
    """
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return True

    from .models import Recipe, App
    Recipe.objects.all().filter(apply_status=Recipe.APPLY_PROGRESS).update(apply_status=Recipe.APPLY_FAILED)
    App.objects.all().update(applying_in_background=False)


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        reset_background_apply()
        return

