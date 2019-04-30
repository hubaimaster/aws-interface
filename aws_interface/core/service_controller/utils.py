import simplejson as json


def make_data(app_id, params, recipe_json, admin=True):
    recipe = json.loads(recipe_json)
    data = {
        'params': params,
        'recipe': recipe,
        'app_id': app_id,
        'admin': admin,
        'user': {
            'id': 'admin-{}'.format(app_id),
            'groups': ['admin'],
            'creationDate': 0,
            'extra': {}
        }
    }
    return data


def lambda_method(func):
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        body = result.get('body', {})
        json_body = json.dumps(body)
        return json.loads(json_body)
    return wrap

