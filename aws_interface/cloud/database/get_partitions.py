
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'items': ['str'],
    },
    'description': 'Get all partitions in system'
}


@NeedPermission(Permission.Run.Database.get_partitions)
def do(data, resource):
    body = {}
    params = data['params']
    partitions = resource.db_get_partitions()
    body['items'] = partitions
    return body
