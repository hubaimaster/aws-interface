from cloud.aws import *
from cloud.crypto import *
import cloud.shortuuid as shortuuid

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'guest_id': 'str?',
    },
    'output_format': {
        'guest_id': 'str',
        'session_id': 'str',
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    guest_id = params.get('guest_id', None)
    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    login_conf = recipe['login_method']['guest_login']
    default_group_name = login_conf['default_group_name']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        response['error'] = '6'
        response['message'] = '게스트 로그인이 비활성화 상태입니다.'
        return response

    dynamo = DynamoDB(boto3)

    if guest_id:
        result = dynamo.get_item(table_name, guest_id)
        if result.get('Item', None):
            session_item = {
                'userId': guest_id
            }
            dynamo.put_item(table_name, 'session', session_item)
            response['message'] = '게스트 로그인 성공'
            return response
        else:
            response['error'] = '7'
            response['message'] = '해당 게스트가 없습니다'
            return response
    else:
        guest_id = shortuuid.uuid()
        email = '{}@guest.com'.format(shortuuid.uuid())
        item = {
            'email': email,
            'group': default_group_name,
            'extra': {},
            'loginMethod': 'guest_login',
        }
        dynamo.put_item(table_name, 'user', item, item_id=guest_id)
        session_id = shortuuid.uuid()
        session_item = {
            'userId': guest_id
        }
        dynamo.put_item(table_name, 'session', session_item, item_id=session_id)
        response['session_id'] = session_id
        response['guest_id'] = guest_id
        response['message'] = '게스트 로그인 성공'
        return response

