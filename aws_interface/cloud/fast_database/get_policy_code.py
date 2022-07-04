
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
import inspect
import time
from cloud.env import safe_to_run_code

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'mode': '"create" | "read" | "update" | "delete"',
    },
    'output_format': {
        'code': 'str',
    },
    'description': 'Get policy code about mode (CRUD)'
}

SERVICE = 'meta-info#database_policy'
cache = {}


def remove_cache():
    global cache
    cache = {}


def match_policy_after_get_policy_code(resource, mode, partition, user, item, new_item={}):
    policy_code = get_policy_code(resource, partition, mode)
    result = match_policy(policy_code, user, item, new_item)
    return result


def match_policy(policy_code, user, item, new_item={}):
    if not safe_to_run_code():
        return True
    exec(policy_code)
    params_len = eval('len(inspect.signature(has_permission).parameters)')
    if params_len == 2:
        result = eval('has_permission(user, item)')
    elif params_len == 3:
        result = eval('has_permission(user, item, new_item)')
    else:
        result = False
    return result


def get_default_policy_code(mode):
    if mode == 'create':
        import cloud.fast_database.policy.create as source
        policy_code = inspect.getsource(source)
    elif mode == 'read':
        import cloud.fast_database.policy.read as source
        policy_code = inspect.getsource(source)
    elif mode == 'update':
        import cloud.fast_database.policy.update as source
        policy_code = inspect.getsource(source)
    elif mode == 'delete':
        import cloud.fast_database.policy.delete as source
        policy_code = inspect.getsource(source)
    else:
        policy_code = None
    return policy_code


def get_policy_code(resource, partition, mode, use_cache=True):
    global cache
    pk = f'{SERVICE}@{partition}'
    sk = f'{mode}'

    # 독자 환경에서만 캐싱 허용, 글로벌이라
    if safe_to_run_code():
        key = f'{pk}{sk}{int(time.time() / 100)}'
        if key in cache and use_cache:
            return cache[key]
    else:
        key = None

    item = resource._fdb_get_item_low_level(pk, sk)
    if item:
        policy_code = item.get('code')
    else:
        """ Assign default item that has default policy code
        """
        policy_code = get_default_policy_code(mode)
    if key:
        cache[key] = policy_code
    return policy_code


@NeedPermission(Permission.Run.FastDatabase.get_policy_code)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = params.get('partition', None)
    mode = params.get('mode', None)

    # 필수 파라메터 체크
    if not partition_to_apply:
        raise errorlist.NEED_PARTITION

    if not mode:
        raise errorlist.NEED_MODE

    policy_code = get_policy_code(resource, partition_to_apply, mode, use_cache=False)
    if policy_code:
        body['code'] = policy_code
    else:
        raise errorlist.NO_SUCH_POLICY_MODE
    return body
