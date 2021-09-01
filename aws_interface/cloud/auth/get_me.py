
from cloud.crypto import Hash
from cloud.permission import Permission, NeedPermission
from cloud.auth.get_user_groups import do as _get_user_groups
from cloud.message import error
from cloud.auth import get_policy_code
from cloud.auth import util
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        '__est': 'str?'
    },
    'output_format': {
        'item?': {
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'groups': ['str'],
        },
    },
    'description': 'Get my information via session'
}


def get_user_groups(data, resource):
    response = _get_user_groups(data, resource)
    groups = response.get('groups', [])
    return groups


def should_session_security_enhancement(data, resource, user):
    """
    세션 보안 강화가 적용된 그룹에 포함되어 있는지 확인
    :param data:
    :param resource:
    :param user:
    :return:
    """
    if not user:
        return False
    user_group_names = user.get('groups', [])
    all_groups = get_user_groups(data, resource)
    all_groups = dict({all_group['name']: all_group for all_group in all_groups})
    for user_group_name in user_group_names:
        group = all_groups.get(user_group_name, None)
        if group and group.get('session_security_enhancement', False):
            return True
    return False


def verify_session_time(session, params):
    """
    세션 보안을 사용할 경우에 (session.use_secure == True)
    session_public_key (spk) 로 params 에서 넘어온 encrypted_session_time (est) 를 검증합니다.
    검증시 알고리즘은 sha3_512 을 사용합니다.
    :param session:
    :param params:
    :return:
    """
    spk = session.get('__spk', None)
    client_est = params.get('__est', None)
    timestamp_offset = session.get('timestamp_offset', 0)

    if not client_est:
        return False
    now = time.time()
    now = int(now)
    # Time window -4~4초
    for offset in range(-4, 5):
        target_plain = now + offset + timestamp_offset
        target_plain = str(target_plain)
        server_est = Hash.sha3_512(target_plain + spk)
        if server_est == client_est:
            return True
    return False


def update_last_access_date(resource, session):
    """
    세션의 마지막 접속일자를 업데이트합니다.
    성능상, 1분 이상 차이날 경우만 업데이트 합니다.
    :param resource:
    :param session:
    :return:
    """
    if session:
        now = int(time.time())
        last_access_date = session.get('last_access_date', 0)
        if abs(now - last_access_date) > 60:
            resource.db_update_item_v2(session['id'], {
                'partition': 'session',
                'last_access_date': now
            })


@NeedPermission(Permission.Run.Auth.get_me)
def do(data, resource, system_call=False):  # Do not check policy when system_call is true
    body = {}
    params = data['params']
    client_ip = data.get('client_ip', None)
    session_id = params.get('session_id', None)

    try:
        if session_id:
            session = resource.db_get_item(Hash.sha3_512(session_id))
            update_last_access_date(resource, session)
        else:
            session = None
    except BaseException as ex:
        body['exception'] = str(ex)
        body['error'] = error.INVALID_SESSION
        return body

    if session:
        user_id = session.get('user_id', None)
    else:
        user_id = None

    if session and session.get('use_secure', False):
        if not verify_session_time(session, params):
            return error.SESSION_NOT_VERIFICATION

    if user_id:
        # 데이터 전송량 및 읽기용량, 시간을 줄이기 위해 프로젝션된 내용만 끌어서 사용
        # user_cache = util.get_cache(user_id)
        # if user_cache:
        #     projection_only_user = resource.db_get_item(user_id, ['id', 'updated_date'])
        #     if projection_only_user:
        #         real_updated_date = projection_only_user.get('updated_date', 0)
        #         cache_updated_date = user_cache.get('updated_date', 0)
        #         if real_updated_date <= cache_updated_date:
        #             user = user_cache.copy()
        #         else:
        #             user = resource.db_get_item(user_id)
        #     else:
        #         user = None
        # else:
        #     user = resource.db_get_item(user_id)
        # # 캐시에 유저 저장
        # if user:
        #     util.set_cache(user_id, user.copy())

        user = resource.db_get_item(user_id)
        if not system_call:
            if not get_policy_code.match_policy_after_get_policy_code(resource, 'read', 'user', user, user):
                body['item'] = None
                body['error'] = error.READ_POLICY_VIOLATION
                return body

        if session.get('client_ip', None) == client_ip:
            body['item'] = user
        else:
            if should_session_security_enhancement(data, resource, user):
                body['item'] = None
                body['error'] = error.SESSION_SECURITY_VIOLATION
                resource.db_delete_item(session['id'])  # Logout
                return body
            else:
                body['item'] = user
                return body
    else:
        body['item'] = None
    return body


if __name__ == '__main__':
    pass
