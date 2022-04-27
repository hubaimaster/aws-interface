
from cloud.crypto import *
from cloud.auth.get_login_method import do as get_login_method
from cloud.permission import Permission, NeedPermission
from cloud.auth.get_login_method import match_policy
from cloud.message import error
from cloud.shortuuid import uuid
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


# 회원 가입 가능한 권한이 있는지 확인합니다.
@NeedPermission(Permission.Run.Auth.register)
def do(data, resource):
    body = {}
    params = data['params']

    email = params['email']
    password = params['password']

    # 추가적으로 삽입할 데이터들을 가져옵니다.
    extra = params.get('extra', {})

    # 빈 값들은 세팅에서 제외합니다.
    extra = {key: value for key, value in extra.items() if value != '' and value != {} and value != []}

    # 높은 암호화 수준을 위해 Salt 를 랜덤 생성합니다.
    salt = Salt.get_salt(32)

    # 사용자가 입력한 password 를 salt 와 함께 sha3_512 으로 해싱합니다.
    password_hash = hash_password(password, salt)

    # 비밀번호 정책 기준을 충족하는지 체크하기 위해 delegate 함수로 비밀번호의 메타 정보를 체크합니다.
    password_meta = {
        'count': len(password),
        'count_lowercase': len([c for c in password if c.islower()]),
        'count_uppercase': len([c for c in password if c.isupper()]),
        'count_special': len([c for c in password if c in string.punctuation]),
    }

    partition = 'user'
    data['params']['login_method'] = 'email_login'
    login_conf = get_login_method(data, resource)['item']

    # 사용자의 가입 정책기준을 가져옵니다.
    register_policy_code = login_conf.get('register_policy_code', None)

    if not data.get('admin', False):
        # 사용자 가입 정책에 부합하는지 확인합니다. 부합하지 않으면 정책 위반 에러를 리턴합니다.
        if not match_policy(register_policy_code, extra, password_meta):
            body['error'] = error.REGISTER_POLICY_VIOLATION
            return body

    # 시스템의 Login config 에 저장된대 기본 가입 그룹 이름을 가져옵니다.
    default_group_name = login_conf['default_group_name']

    # 시스템에서 로그인이 허용되는지 체크합니다.
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    # 로그인 허용이 되지 않는 경우입니다.
    if not enabled:
        body['error'] = error.EMAIL_LOGIN_INVALID
        return body

    # email 로 사용자가 있는지 확인합니다.
    instructions = [
        [None, 'email', 'eq', email]
    ]
    items, end_key = resource.db_query(partition, instructions)
    users = list(items)

    # 이미 해당 이메일로 가입된 멤버가 있는 경우
    if len(users) > 0:
        body['error'] = error.EXISTING_ACCOUNT
        return body
    else:
        # 해싱된 비밀번호로 회원 가입을 진행합니다.
        item = {
            'id': str(uuid()),
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
        resource.db_put_item(partition, item, item_id=item['id'])
        body['item'] = item
        return body
