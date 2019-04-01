
from cloud.crypto import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'password': 'str',
        'extra': 'map'
    },
    'output_format': {
        'success': 'bool',
        'message': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']

    email = params['email']
    password = params['password']
    extra = params.get('extra', {})

    salt = Salt.get_salt(32)
    password_hash = hash_password(password, salt)

    partition = 'user'
    default_group_name = 'admin'

    instructions = [
        (None, ('eq', 'email', email))
    ]
    items, end_key = resource.db_query('user', instructions)
    users = items
    if len(users) > 0:
        body['message'] = '이미 가입된 회원이 존재합니다.'
        body['success'] = False
        return Response(body)
    else:
        item = {
            'email': email,
            'passwordHash': password_hash,
            'salt': salt,
            'group': default_group_name,
            'extra': extra,
            'loginMethod': 'email_login',
        }
        resource.db_put_item(partition, item)
        body['message'] = '회원가입에 성공하였습니다.'
        body['success'] = True
        return Response(body)
