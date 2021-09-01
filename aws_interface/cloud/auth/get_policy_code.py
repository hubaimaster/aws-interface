
from cloud.permission import Permission, NeedPermission
from cloud.message import error
import inspect
import time
from cloud.env import safe_to_run_code

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition_to_apply': 'str',
        'mode': '"read" | "update"',
    },
    'output_format': {
        'policy_code?': 'str',
    },
    'description': 'Get policy code about mode (RU)'
}

SERVICE = 'auth'
cache = {}


def match_policy_after_get_policy_code(resource, mode, partition, user, item):
    policy_code = get_policy_code(resource, partition, mode)
    result = match_policy(policy_code, user, item)
    return result


def match_policy(policy_code, user, item):
    if not safe_to_run_code():
        return True
    exec(policy_code)
    result = eval('has_permission(user, item)')
    return result


def get_default_policy_code(mode):
    if mode == 'read':
        import cloud.auth.policy.read as source
        policy_code = inspect.getsource(source)
    elif mode == 'update':
        import cloud.auth.policy.update as source
        policy_code = inspect.getsource(source)
    else:
        policy_code = None
    return policy_code


def get_policy_code(resource, partition, mode, use_cache=True):
    item_id = '{}-policy-{}-{}'.format(SERVICE, partition, mode)

    # 캐싱
    key = '{}-{}'.format(item_id, int(time.time() / 100))
    if key in cache and use_cache:
        return cache[key]

    item = resource.db_get_item(item_id)
    if item:
        policy_code = item.get('code')
    else:
        """ Assign default item that has default policy code
        """
        policy_code = get_default_policy_code(mode)

    cache[key] = policy_code
    return policy_code


@NeedPermission(Permission.Run.Auth.get_policy_code)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = params.get('partition_to_apply')
    mode = params.get('mode')

    policy_code = get_policy_code(resource, partition_to_apply, mode, use_cache=False)
    if policy_code:
        body['code'] = policy_code
    else:
        body['error'] = error.NO_SUCH_POLICY_MODE
    return body
