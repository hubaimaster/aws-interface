import json
import importlib
from abc import ABCMeta


class RecipeController(metaclass=ABCMeta):
    """
    Make sure to set RECIPE when you inherit this class.
    """
    RECIPE = None

    def __init__(self):
        """
        To add recipe-specific actions, override __init__. Make sure to
        CALL THIS BASE __init__ FUNCTION.
        """
        self.data = dict()
        assert (type(self).RECIPE is not None)
        self.data['recipe_type'] = type(self).RECIPE

    def to_json(self):
        return json.dumps(self.data)

    def load_json_string(self, json_string):
        self.data = json.loads(json_string)

    def get_recipe(self):
        return type(self).RECIPE

    def put_cloud_api(self, name, module, permissions=['all']):  # 'cloud.auth.login'
        """
        Activate cloud api (add field within recipe data dict)

        :param name:
        E.g., 'login'

        :param module:
        E.g., 'cloud.auth.login'

        :param permissions:
        List of groups who has API call permission

        :return:
        """
        if 'cloud_apis' not in self.data:
            self.data['cloud_apis'] = {}
        try:
            info = importlib.import_module(module).info
        except AttributeError:
            print('{} module does not have an info variable'.format(name))
            info = {}
        self.data['cloud_apis'][name] = {
            'name': name,
            'permissions': permissions,
            'module': module,
            'info': info
        }
        return True

    def get_cloud_apis(self):
        cloud_apis = self.data.get('cloud_apis', {})
        return cloud_apis.values()
