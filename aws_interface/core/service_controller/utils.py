import simplejson as json
import time


def make_data(app_id, params, admin=True):
    data = {
        'params': params,
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
        current_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - current_time
        if result:
            body = result.get('body', {})
            body['duration'] = duration
            json_body = json.dumps(body)
            return json.loads(json_body)
    return wrap

