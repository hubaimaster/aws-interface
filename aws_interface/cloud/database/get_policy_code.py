
from cloud.permission import Permission, NeedPermission
from cloud.message import error
import inspect
import os

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition_to_apply': 'str',
        'mode': '"create" | "read" | "update" | "delete" | "query" | "join" | "index"',
    },
    'output_format': {
        'policy_code?': 'str',
    },
    'description': 'Get policy code about mode (CRUD)'
}

SERVICE = 'database'


def match_policy_after_get_policy_code(resource, mode, partition, user, item):
    policy_code = get_policy_code(resource, partition, mode)
    result = match_policy(policy_code, user, item)
    return result


def match_policy(policy_code, user, item):
    # if user and 'admin' in user.get('groups', []):
    #     return True
    os_env = os.environ.get('AWS_EXECUTION_ENV', None)
    # if os_env is None:
    #     return True
    exec(policy_code)
    result = eval('has_permission(user, item)')
    return result


def run_policy(policy_code, user, item):
    os_env = os.environ.get('AWS_EXECUTION_ENV', None)
    if os_env is None:
        return False
    exec(policy_code)
    result = eval('has_permission(user, item)')
    return result


def get_policy_code(resource, partition, mode):
    item_id = '{}-policy-{}-{}'.format(SERVICE, partition, mode)
    item = resource.db_get_item(item_id)
    if item:
        policy_code = item.get('code')
    else:
        """ Assign default item that has default policy code
        """
        if mode == 'create':
            import cloud.database.policy.create as source
            policy_code = inspect.getsource(source)
        elif mode == 'read':
            import cloud.database.policy.read as source
            policy_code = inspect.getsource(source)
        elif mode == 'update':
            import cloud.database.policy.update as source
            policy_code = inspect.getsource(source)
        elif mode == 'delete':
            import cloud.database.policy.delete as source
            policy_code = inspect.getsource(source)
        elif mode == 'query':
            import cloud.database.policy.query as source
            policy_code = inspect.getsource(source)
        elif mode == 'join':
            import cloud.database.policy.join as source
            policy_code = inspect.getsource(source)
        elif mode == 'index':
            import cloud.database.policy.index as source
            policy_code = inspect.getsource(source)
        else:
            policy_code = None
    return policy_code


@NeedPermission(Permission.Run.Database.get_policy_code)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = params.get('partition_to_apply')
    mode = params.get('mode')

    policy_code = get_policy_code(resource, partition_to_apply, mode)
    if policy_code:
        body['code'] = policy_code
    else:
        body['error'] = error.NO_SUCH_POLICY_MODE
    return body
