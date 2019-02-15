import urllib
import cgi
import json
import importlib
import boto3
import cloud.auth.get_me as get_me


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
    params = event
    print('params:', params)

    cloud_api_name = params.get('cloud_api_name', None)
    
    with open('./cloud/recipe.json', 'r') as f:
        recipe = json.load(f)
      
    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()
        
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

    user = get_me.do(data, boto3).get('body', {}).get('item', None)
    data['user'] = user

    module = importlib.import_module(module_name)
    if 'all' in permissions:
        module_response = module.do(data, boto3)
    elif user.get('group', None) in permissions:
        module_response = module.do(data, boto3)
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
    return response
