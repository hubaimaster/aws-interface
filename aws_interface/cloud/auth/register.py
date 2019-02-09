from cloud.aws import *
from cloud.crypto import *


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'password': 'str',
        'extra': 'map'
    },
    'output_format': {
        'message': 'str',
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    email = params['email']
    password = params['password']
    extra = params.get('extra', {})

    salt = Salt.get_salt(32)
    password_hash = hash_password(password, salt)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)  # Should be auth-143..
    partition = 'user'
    login_conf = recipe['login_method']['email_login']
    default_group_name = login_conf['default_group_name']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        response['error'] = '4'
        response['message'] = '이메일 로그인이 비활성화 상태입니다.'
        return response

    dynamo = DynamoDB(boto3)
    resp = dynamo.get_items_with_index(table_name, 'partition-email', 'partition', 'user', 'email', email)
    users = resp['Items']
    if len(users) > 0:
        response['message'] = '이미 가입된 회원이 존재합니다.'
        response['error'] = '1'
        return response
    else:
        item = {
            'email': email,
            'passwordHash': password_hash,
            'salt': salt,
            'group': default_group_name,
            'extra': extra,
            'loginMethod': 'email_login',
        }
        dynamo.put_item(table_name, partition, item)
        response['message'] = '회원가입에 성공하였습니다.'
        return response
