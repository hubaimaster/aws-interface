
from cloud.crypto import *
import cloud.auth.get_login_method as get_login_method
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth.get_login_method import match_policy
import urllib.request
import json
from cloud.auth.util import already_has_account_email
from cloud.shortuuid import uuid


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'access_token': 'str',
    },
    'output_format': {
        'session_id': 'str',
    },
    'description': 'Sign-in by access_token from naver login sdk'
}


def get_naver_profile_response(access_token):
    token = access_token
    header = "Bearer " + token  # Bearer 다음에 공백 추가
    url = "https://openapi.naver.com/v1/nid/me"
    request = urllib.request.Request(url)
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        response_body = response_body.decode('utf8')
        response_body = json.loads(response_body)
        result = response_body.get('response')
        return result
    # {'id': '11637256',
    # 'nickname': '자유',
    # 'profile_image': 'https://phinf.pstatic.net/contact/20180107_94/1515294280098yI5z4_JPEG/0.jpg',
    # 'age': '20-29',
    # 'gender': 'M',
    # 'email': 'kchdully@naver.com',
    # 'name': '김창환',
    # 'birthday': '08-12'}
    else:
        print("Error Code:" + rescode)
        return None


def create_session(resource, user, data):
    user_id = user['id']
    session_id = token_urlsafe(32)
    session_item = {
        'user_id': user_id,
        'session_type': 'naver_login',
        'client_ip': data.get('client_ip', None)
    }
    _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


@NeedPermission(Permission.Run.Auth.login_naver)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    access_token = params.get('access_token')
    data['params']['login_method'] = 'naver_login'
    login_conf = get_login_method.do(data, resource)['item']
    default_group_name = login_conf['default_group_name']
    register_policy_code = login_conf.get('register_policy_code', None)

    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.NAVER_LOGIN_INVALID
        return body

    extra_response = get_naver_profile_response(access_token)
    naver_user_id = extra_response['id']
    naver_user_email = extra_response['email']

    if not data.get('admin', False):
        if not match_policy(register_policy_code, extra_response, None):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    instructions = [
        (None, ('naver_user_id', 'eq', naver_user_id)),
        ('and', ('login_method', 'eq', 'naver_login')),
    ]
    items, end_key = resource.db_query('user', instructions)
    if items:
        session_id = create_session(resource, items[0], data)
        body['user_id'] = items[0]['id']
        body['session_id'] = session_id
        body['is_first_login'] = False
        return body
    elif not already_has_account_email(naver_user_email, resource):  # Create new user and create session also.
        item = {
            'id': str(uuid()),
            'email': naver_user_email,
            'groups': [default_group_name],
            'login_method': 'naver_login',
            'naver_user_id': naver_user_id,
        }
        # Put extra value in the item
        key_map = {'nickname': 'name',
                   'profile_image': 'profile_image'}
        for key in extra_response:
            if key not in item:
                if key in key_map:
                    item[key_map[key]] = extra_response[key]
                else:
                    item[key] = extra_response[key]
        resource.db_put_item('user', item, item.get('id'))
        session_id = create_session(resource, item, data)
        body['session_id'] = session_id
        body['user_id'] = item['id']
        body['is_first_login'] = True
        return body
    else:
        body['error'] = error.EXISTING_ACCOUNT_VIA_OTHER_LOGIN_METHOD
        return body

