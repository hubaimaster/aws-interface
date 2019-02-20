import json
import importlib
from abc import ABCMeta


class RecipeController(metaclass=ABCMeta):
    """
    Make sure to set RECIPE_TYPE when you inherit this class.
    """
    RECIPE_TYPE = None

    def __init__(self):
        """
        To add recipe-specific actions, override __init__. Make sure to
        CALL THIS BASE __init__ FUNCTION.
        """
        self.data = dict()
        assert (type(self).RECIPE_TYPE is not None)
        self.data['recipe_type'] = type(self).RECIPE_TYPE

    def to_json(self):
        return json.dumps(self.data)

    def load_json_string(self, json_string):
        self.data = json.loads(json_string)
        # self.common_init() this should be named something like update()
        # currently, there is no use for this
        # consider redesigning the __init__ function to accept a data variable

    def get_recipe_type(self):
        return type(self).RECIPE_TYPE

    def put_cloud_api(self, name, module, permissions=['all']):  # 'cloud.auth.login'
        if 'cloud_apis' not in self.data:
            self.data['cloud_apis'] = {}
        try:
            info = importlib.import_module(module).info
        except:
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
