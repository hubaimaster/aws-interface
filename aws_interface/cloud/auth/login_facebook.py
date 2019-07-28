
from cloud.crypto import *
import cloud.auth.get_login_method as get_login_method
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth.get_login_method import match_policy
from botocore.vendored.requests import get
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'access_token': 'str',
    },
    'output_format': {
        'session_id': 'str',
    },
    'description': 'Sign-in by access_token from facebook sdk [scopes=id,email]'
}


def get_facebook_response(access_token, scopes=['id', 'email']):
    fields = '%2C'.join(scopes)
    url = "https://graph.facebook.com/v3.3/me?fields={}&access_token={}".format(fields, access_token)
    response = get(url)
    return json.loads(response.content)


def create_session(resource, user):
    user_id = user['id']
    session_id = token_urlsafe(32)
    session_item = {
        'user_id': user_id,
        'session_type': 'facebook_login',
    }
    _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


@NeedPermission(Permission.Run.Auth.login_facebook)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    access_token = params.get('access_token')
    data['params']['login_method'] = 'facebook_login'
    login_conf = get_login_method.do(data, resource)['item']
    default_group_name = login_conf['default_group_name']
    register_policy_code = login_conf.get('register_policy_code', None)

    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.EMAIL_LOGIN_INVALID
        return body

    extra_fb_response = get_facebook_response(access_token, ['id', 'email'])
    fb_user_id = extra_fb_response['id']
    fb_user_email = extra_fb_response['email']

    if not data.get('admin', False):
        if not match_policy(register_policy_code, extra_fb_response, None):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    instructions = [
        (None, ('fb_user_id', 'eq', fb_user_id)),
        ('and', ('login_method', 'eq', 'facebook_login')),
    ]
    items, end_key = resource.db_query('user', instructions)
    if items:
        session_id = create_session(resource, items[0])
        body['session_id'] = session_id
        return body
    else:  # Create new user and create session also.
        item = {
            'email': fb_user_email,
            'groups': [default_group_name],
            'login_method': 'facebook_login',
            'fb_user_id': fb_user_id,
        }
        # Put extra value in the item
        for key in extra_fb_response:
            if key not in item:
                item[key] = extra_fb_response[key]
        resource.db_put_item('user', item)
        session_id = create_session(resource, item)
        body['session_id'] = session_id
        return body

