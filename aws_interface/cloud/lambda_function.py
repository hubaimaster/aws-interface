import urllib
import cgi
import json
import decimal
import importlib
import boto3


def get_response_header():
    api_gateway_response_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With',
        'Access-Control-Allow-Credentials': True,
        'Content-Type': 'application/json'
    }
    return api_gateway_response_header


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


def put_response(response, key, value):
    if response['body'] is None:
        response['body'] = {}
        response['body'] = json.dumps(response['body'])
    response['body'] = json.loads(response['body'])
    response['body'][key] = value
    response['body'] = json.dumps(response['body'], default=decimal_default)


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


def make_event(params):
    event = dict()
    event['queryStringParameters'] = params
    return event


def handler(event, context):
    response = {
        'statusCode': 200,
        'headers': get_response_header(),
        'body': None,
    }
    parmas = event
    cloud_api_name = parmas.get('cloud_api_name', None)
    with open('./cloud/recipe.json', 'r') as file:
        recipe = file.read()
        recipe = json.loads(recipe)
        print('recipe:', type(recipe))

    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()

    cloud_apis = recipe.get('cloud_apis', {})
    cloud_api = cloud_apis.get(cloud_api_name, {})
    module_name = cloud_api.get('module', None)
    permissions = cloud_api.get('permissions', [])

    data = {
        'params': parmas,
        'recipe': recipe,
        'app_id': app_id,
        'admin': False,
    }
    print('permissions:', permissions)
    if 'all' in permissions:
        module = importlib.import_module(module_name)
        body = module.do(data, boto3)
    else:
        import cloud.auth.get_me as get_me
        me = get_me.do(data, boto3).get('item', None)
        if me.get('group', None) in permissions:
            module = importlib.import_module(module_name)
            body = module.do(data, boto3)

    response['body'] = body
    return response
