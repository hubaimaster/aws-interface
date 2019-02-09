from cloud.aws import *
from cloud.crypto import *
import cloud.shortuuid as shortuuid

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'password': 'str'
    },
    'output_format': {
        'message': 'str',
        'error': 'str',
        'session_id': 'str',
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    email = params.get('email', None)
    password = params.get('password', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    login_conf = recipe['login_method']['email_login']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        response['error'] = '5'
        response['message'] = '이메일 로그인이 비활성화 상태입니다.'
        return response

    dynamo = DynamoDB(boto3)
    result = dynamo.get_items_with_index(table_name, 'partition-email', 'partition', 'user', 'email', email)
    items = result.get('Items', [])
    if len(items) > 0:
        user = items[0]
        password_hash = user['passwordHash']
        salt = user['salt']
        if password_hash == hash_password(password, salt):
            user_id = user['id']
            session_id = shortuuid.uuid()
            session_item = {
                'userId': user_id,
            }
            dynamo.put_item(table_name, 'session', session_item, item_id=session_id)
            response['session_id'] = session_id
            response['message'] = '로그인 성공'
        else:
            response['message'] = '비밀번호가 틀립니다.'
            response['error'] = '2'
    else:
        response['message'] = '해당 계정이 존재하지 않습니다.'
        response['error'] = '1'
    return response
