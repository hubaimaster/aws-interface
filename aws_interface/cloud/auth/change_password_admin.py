
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
        'user_id': 'str',
        'new_password': 'str',
    },
    'output_format': {
        'user_id?': 'str',
    },
    'description': 'Change password to new_password'
}


@NeedPermission(Permission.Run.Auth.change_password_admin)
def do(data, resource):
    body = {}
    params = data['params']
    user_id = params.get('user_id')
    new_password = params.get('new_password')

    user = resource.db_get_item(user_id)
    if user.get('partition', None) != 'user':
        body['error'] = error.NOT_USER_PARTITION
        body['success'] = False
        return body

    salt = user['salt']
    data['params']['login_method'] = 'email_login'

    new_password_hash = hash_password(new_password, salt)
    # user['password_hash'] = new_password_hash
    user_id = user.get('id')
    success = resource.db_update_item_v2(user_id, {
        'partition': 'user',
        'password_hash': new_password_hash,
        'updated_date': float(time.time())
    })
    body['user_id'] = user.get('id')
    body['success'] = success
    return body
