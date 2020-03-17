
from cloud.crypto import *
import cloud.auth.get_login_method as get_login_method
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth.get_login_method import match_policy
import json
import urllib.request
from cloud.auth.util import already_has_account_email
from cloud.shortuuid import uuid


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'id_token': 'str',
    },
    'output_format': {
        'session_id': 'str',
    },
    'description': 'Sign-in by id_token from google sdk'
}


def get_google_profile_response(id_token):
    token = id_token
    url = "https://oauth2.googleapis.com/tokeninfo?id_token={}".format(token)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        response_body = response_body.decode('utf8')
        response_body = json.loads(response_body)
        return response_body
    # {'iss': 'https://accounts.google.com',
    # 'azp': '172334229458-k29fj2gh551317cj4m3ehqs0f4rlpt9m.apps.googleusercontent.com',
    # 'aud': '172334229458-cag7vkta9bcdlhildi1atvp2hcpac2hc.apps.googleusercontent.com',
    # 'sub': '114048331009697405080',
    # 'email': 'kchdully@gmail.com',
    # 'email_verified': 'true',
    # 'name': '김창환',
    # 'picture': 'https://lh3.googleusercontent.com/a-/AOh14GjG7x03-IEkzwziE2j_s91qxeWY43kmC48qb4MgiA=s96-c',
    # 'given_name': '창환',
    # 'family_name': '김',
    # 'locale': 'ko',
    # 'iat': '1583690625',
    # 'exp': '1583694225',
    # 'alg': 'RS256',
    # 'kid': 'cb404383844b46312769bb929ecec57d0ad8e3bb',
    # 'typ': 'JWT'}
    else:
        print("Error Code:" + rescode)
        return None


def create_session(resource, user):
    user_id = user['id']
    session_id = token_urlsafe(32)
    session_item = {
        'user_id': user_id,
        'session_type': 'google_login',
    }
    _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


@NeedPermission(Permission.Run.Auth.login_google)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    id_token = params.get('id_token')
    data['params']['login_method'] = 'google_login'
    login_conf = get_login_method.do(data, resource)['item']
    default_group_name = login_conf['default_group_name']
    register_policy_code = login_conf.get('register_policy_code', None)

    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.GOOGLE_LOGIN_INVALID
        return body

    extra_response = get_google_profile_response(id_token)
    google_user_id = extra_response['sub']
    google_user_email = extra_response['email']

    if not data.get('admin', False):
        if not match_policy(register_policy_code, extra_response, None):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    instructions = [
        (None, ('google_user_id', 'eq', google_user_id)),
        ('and', ('login_method', 'eq', 'google_login')),
    ]
    items, end_key = resource.db_query('user', instructions)
    if items:
        session_id = create_session(resource, items[0])
        body['session_id'] = session_id
        return body
    elif not already_has_account_email(google_user_email, resource):  # Create new user and create session also.
        item = {
            'id': uuid(),
            'email': google_user_email,
            'groups': [default_group_name],
            'login_method': 'google_login',
            'google_user_id': google_user_id,
        }
        # Put extra value in the item
        for key in extra_response:
            if key not in item:
                item[key] = extra_response[key]
        resource.db_put_item('user', item)
        session_id = create_session(resource, item)
        body['session_id'] = session_id
        return body
    else:
        body['error'] = error.EXISTING_ACCOUNT_VIA_OTHER_LOGIN_METHOD
        return body
