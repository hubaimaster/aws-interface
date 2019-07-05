
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition_to_apply': 'str',
        'mode': '"create" | "read" | "update" | "delete"',
        'policy_code': 'str',
    },
    'output_format': {

    },
    'description': 'Put policy in the partition'
}

SERVICE = 'database'
POLICY_MODES = ['create', 'read', 'update', 'delete']


@NeedPermission(Permission.Run.Database.put_policy)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = params.get('partition_to_apply')
    mode = params.get('mode')
    code = params.get('code')

    if mode not in POLICY_MODES:
        body['error'] = error.NO_SUCH_POLICY_MODE
        return Response(body)

    item_id = '{}-policy-{}-{}'.format(SERVICE, partition_to_apply, mode)
    item = {
        'partition_to_apply': partition_to_apply,
        'mode': mode,
        'code': code,
    }
    resource.db_put_item('{}-policy'.format(SERVICE), item, item_id)
    return Response(body)
