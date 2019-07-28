
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Delete partition'
}


@NeedPermission(Permission.Run.Database.delete_partition)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params.get('partition', None)
    success = resource.db_delete_partition(partition)
    body['success'] = success
    return body
