
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'mode': 'str: "read" | "write"',
        'policy_code': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Put policy code used for create, read, delete operation'
}

SERVICE = 'storage'
POLICY_MODES = ['create', 'read', 'delete']


@NeedPermission(Permission.Run.Storage.put_policy)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = 'files'
    mode = params.get('mode')
    code = params.get('code')

    if mode not in POLICY_MODES:
        body['error'] = error.NO_SUCH_POLICY_MODE
        return body

    item_id = '{}-policy-{}-{}'.format(SERVICE, partition_to_apply, mode)
    item = {
        'partition_to_apply': partition_to_apply,
        'mode': mode,
        'code': code,
    }
    success = resource.db_put_item('{}-policy'.format(SERVICE), item, item_id)
    body['success'] = success
    return body
