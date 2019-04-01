import urllib
import cgi
import json
import importlib
import boto3
import cloud.auth.get_me as get_me
from resource import get_resource

import sys


def get_params(event):
    params = event.get('queryStringParameters', None)
    body = event.get('body', None)
    if params is None:
        params = {}
    if body is not None and len(body) > 0:
        pairs = body.split('&')
        for pair in pairs:
            pair = pair.split('=')
            param = pair[1]
            param = urllib.parse.unquote(param)
            param = cgi.escape(param)
            params[pair[0]] = param
    return params


def handler(event, context):
    import timeit
    start = timeit.default_timer()

    params = event
    recipe_key = params.get('recipe_key', None)
    cloud_api_name = params.get('cloud_api_name', None)

    with open('./cloud/recipes.json', 'r') as f:
        recipes = json.load(f)
      
    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()

    with open('./cloud/vendor.txt', 'r') as file:
        vendor = file.read().strip()

    recipe = recipes[recipe_key]
    cloud_apis = recipe.get('cloud_apis', {})
    cloud_api = cloud_apis.get(cloud_api_name, {})
    module_name = cloud_api.get('module')
    permissions = cloud_api.get('permissions', [])

    data = {
        'params': params,
        'recipe': recipe,
        'app_id': app_id,
        'admin': False,
    }

    """ <<< This code should be changed on the other machine of vendor """
    boto_session = boto3.Session()
    resource = get_resource(vendor, None, app_id, boto_session)
    """ >>> """

    user = get_me.do(data, resource).get('body', {}).get('item', None)
    data['user'] = user

    module = importlib.import_module(module_name)
    sys.modules[module_name] = module

    if 'all' in permissions:
        module_response = module.do(data, resource)
    elif user.get('group', None) in permissions:
        module_response = module.do(data, resource)
    else:
        module_response = {
            'statusCode': 201,
            'body': {
                'message': 'permission denied'
            }
        }

    response = {
        'statusCode': module_response.get('statusCode', 200),
        'headers': module_response.get('header', {}),
        'body': module_response.get('body', {}),
    }

    stop = timeit.default_timer()
    print('Run time:', stop - start)
    return response
