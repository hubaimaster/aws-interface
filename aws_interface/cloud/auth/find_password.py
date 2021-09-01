
from cloud.message import error
from cloud.crypto import *
from cloud.auth.get_login_method import do as get_login_method
from cloud.permission import Permission, NeedPermission
from cloud.auth.get_login_method import match_policy
import string
import time


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'verification_code': 'str?',
        'new_password': 'str?',
    },
    'output_format': {
        'user_id?': 'str',
        'message': 'str',
    },
    'description': '1. Send verification code to email, 2. Enter the verification code and new_password'
}


@NeedPermission(Permission.Run.Auth.find_password)
def do(data, resource):
    body = {}
    user = data['user']
    params = data['params']

    current_password = params.get('current_password')
    new_password = params.get('new_password')

    password_hash = user['password_hash']
    salt = user['salt']

    data['params']['login_method'] = 'email_login'
    login_conf = get_login_method(data, resource)['item']
    register_policy_code = login_conf.get('register_policy_code', None)

    password_meta = {
        'count': len(new_password),
        'count_lowercase': len([c for c in new_password if c.islower()]),
        'count_uppercase': len([c for c in new_password if c.isupper()]),
        'count_special': len([c for c in new_password if c in string.punctuation]),
    }

    if not data.get('admin', False):
        if not match_policy(register_policy_code, {}, password_meta):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    if hash_password(current_password, salt) == password_hash:
        new_password_hash = hash_password(new_password, salt)
        user['password_hash'] = new_password_hash
        user['updated_date'] = float(time.time())
        user_id = user.get('id')
        success = resource.db_update_item(user_id, user)
        body['user_id'] = user.get('id')
        body['success'] = success
    else:
        body['error'] = error.PERMISSION_DENIED
    return body
