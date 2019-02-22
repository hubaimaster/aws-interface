import sys
from django.apps import AppConfig
import warnings


def reset_background_apply(app_config):
    """
    If the server was interrupted while a Recipe was getting
    initialized, indicate that the initialization has failed.

    Requires overhaul, as DB access during AppConfig.reset() is not recommended
    :return:
    """
    exempt_commands = [
        'makemigrations',
        'migrate',
        'test',
    ]

    print(sys.argv)

    for command in exempt_commands:
        if command in sys.argv:
            return True

    try:
        Recipe = app_config.get_model('Recipe')
        App = app_config.get_model('App')
        print('Got models for reset_background_apply()')
        Recipe.objects.all().filter(apply_status=Recipe.APPLY_PROGRESS).update(apply_status=Recipe.APPLY_FAILED)
        App.objects.all().update(applying_in_background=False)
    except LookupError:
        warnings.warn('reset_background_apply() may have an issue. plz submit report to Namgyu')


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        reset_background_apply(self)
        return

