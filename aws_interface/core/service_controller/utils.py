import json


def make_data(app_id, params, recipe_json, admin=True):
    recipe = json.loads(recipe_json)
    data = {
        'params': params,
        'recipe': recipe,
        'app_id': app_id,
        'admin': admin,
        'user': {
            'id': 'admin-{}'.format(app_id),
            'group': 'admin',
            'creationDate': 0,
            'extra': {}
        }
    }
    return data


def lambda_method(func):
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.get('body', {})
    return wrap

