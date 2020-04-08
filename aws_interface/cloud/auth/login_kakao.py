
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
    'description': 'Sign-in by access_token from kakao login sdk'
}


def get_kakao_profile_response(access_token):
    token = access_token
    header = "Bearer " + token  # Bearer 다음에 공백 추가
    url = "https://kapi.kakao.com/v2/user/me"
    request = urllib.request.Request(url)
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        response_body = response_body.decode('utf8')
        response_body = json.loads(response_body)
        return response_body
    # {
    #   "id":123456789,
    #   "properties":{
    #      "nickname":"홍길동카톡",
    #      "thumbnail_image":"http://xxx.kakao.co.kr/.../aaa.jpg",
    #      "profile_image":"http://xxx.kakao.co.kr/.../bbb.jpg",
    #      "custom_field1":"23",
    #      "custom_field2":"여"
    #      ...
    #   },
    #   "kakao_account": {
    #     "profile_needs_agreement": false,
    #     "profile": {
    #       "nickname": "홍길동",
    #       "thumbnail_image_url": "http://yyy.kakao.com/.../img_110x110.jpg",
    #       "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg"
    #     },
    #     "email_needs_agreement":false,
    #     "is_email_valid": true,
    #     "is_email_verified": true,
    #     "email": "xxxxxxx@xxxxx.com"
    #     "age_range_needs_agreement":false,
    #     "age_range":"20~29",
    #     "birthday_needs_agreement":false,
    #     "birthday":"1130",
    #     "birthday_type":"SOLAR",
    #     "gender_needs_agreement":false,
    #     "gender":"female"
    #   }
    # }
    else:
        print("Error Code:" + rescode)
        return None


def create_session(resource, user):
    user_id = user['id']
    session_id = token_urlsafe(32)
    session_item = {
        'user_id': user_id,
        'session_type': 'kakao_login',
    }

    _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


@NeedPermission(Permission.Run.Auth.login_kakao)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    access_token = params.get('access_token')
    data['params']['login_method'] = 'kakao_login'
    login_conf = get_login_method.do(data, resource)['item']
    default_group_name = login_conf['default_group_name']
    register_policy_code = login_conf.get('register_policy_code', None)

    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.KAKAO_LOGIN_INVALID
        return body

    extra_response = get_kakao_profile_response(access_token)
    kakao_user_id = extra_response['id']
    kakao_user_email = extra_response['kakao_account']['email']
    name = extra_response['kakao_account'].get('profile', {}).get('nickname', None)

    if not data.get('admin', False):
        if not match_policy(register_policy_code, extra_response, None):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    instructions = [
        (None, ('kakao_user_id', 'eq', kakao_user_id)),
        ('and', ('login_method', 'eq', 'kakao_login')),
    ]
    items, end_key = resource.db_query('user', instructions)
    if items:
        session_id = create_session(resource, items[0])
        body['session_id'] = session_id
        body['is_first_login'] = False
        return body
    elif not already_has_account_email(kakao_user_email, resource):  # Create new user and create session also.
        item = {
            'id': uuid(),
            'email': kakao_user_email,
            'groups': [default_group_name],
            'login_method': 'kakao_login',
            'kakao_user_id': kakao_user_id,
            'name': name
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
        session_id = create_session(resource, item)
        body['session_id'] = session_id
        body['is_first_login'] = True
        return body
    else:
        body['error'] = error.EXISTING_ACCOUNT_VIA_OTHER_LOGIN_METHOD
        return body