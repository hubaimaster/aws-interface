
from cloud.crypto import *
from cloud.auth.get_login_method import do as get_login_method
from cloud.permission import Permission, NeedPermission
from cloud.auth.get_login_method import match_policy
from cloud.message import error
import string

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'password': 'str',
        'extra?': 'map'
    },
    'output_format': {
        'item?': {
            'id': 'str',
            'creation_date': 'float',
            'email': 'str',
            'login_method': 'str',
            '...': '...'
        }
    },
    'description': 'Register by email and password'
}


@NeedPermission(Permission.Run.Auth.register)
def do(data, resource):
    body = {}
    params = data['params']

    email = params['email']
    password = params['password']
    extra = params.get('extra', {})

    salt = Salt.get_salt(32)
    password_hash = hash_password(password, salt)
    password_meta = {
        'count': len(password),
        'count_lowercase': len([c for c in password if c.islower()]),
        'count_uppercase': len([c for c in password if c.isupper()]),
        'count_special': len([c for c in password if c in string.punctuation]),
    }

    partition = 'user'
    data['params']['login_method'] = 'email_login'
    login_conf = get_login_method(data, resource)['item']
    register_policy_code = login_conf.get('register_policy_code', None)

    if not data.get('admin', False):
        if not match_policy(register_policy_code, extra, password_meta):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    default_group_name = login_conf['default_group_name']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.EMAIL_LOGIN_INVALID
        return body

    instructions = [
        (None, ('email', 'eq', email))
    ]
    items, end_key = resource.db_query(partition, instructions)
    users = list(items)
    if len(users) > 0:
        body['error'] = error.EXISTING_ACCOUNT
        return body
    else:
        item = {
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
            'groups': [default_group_name],
            'login_method': 'email_login',
        }
        # Put extra value in the item
        for key in extra:
            if key not in item:
                item[key] = extra[key]
        resource.db_put_item(partition, item)
        body['item'] = item
        return body
