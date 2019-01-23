import urllib
import cgi
import json
import decimal


def get_response_header():
    api_gateway_response_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With',
        'Access-Control-Allow-Credentials': True,
        'Content-Type': 'application/json'
    }
    return api_gateway_response_header


def get_message(code, nation):
    nation_codes = {
        'en': {
            '0': 'Success',
            '1': 'Invalid session',
            '2': 'User already exists',
            '3': 'Invalid permission',
            '4': 'This account does not exist'
        },
        'ko': {
            '0': '성공',
            '1': '만료된 세션입니다',
            '2': '이미 가입되어있는 회원입니다',
            '3': '권한이 없습니다',
            '4': '해당 계정이 존재하지 않습니다'
        },
    }
    if nation not in nation_codes or code not in nation_codes[nation]:
        return 'Unknown error'
    return {
        'code': code,
        'text': nation_codes[nation][code]
    }


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


def put_response_message(response, code, nation='ko'):
    put_response(response, 'message', get_message(code, nation))


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


def get_param(event, key):
    param = get_params(event).get(key, None)
    return param


def get_event(params):
    event = {}
    event['queryStringParameters'] = params
    return event


def lambda_handler(event, context):
    response = {
        'statusCode': 200,
        'headers': get_response_header(),
        'body': None,
    }
    parmas = get_params(event)
    data = {
        'params': parmas
    }
    import cloud.auth.me as code
    body = code.do(data)
    response['body'] = body
    return response
