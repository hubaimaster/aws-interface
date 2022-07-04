
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'partitions': 'list',
    },
    'description': 'List partitions'
}


@NeedPermission(Permission.Run.FastDatabase.get_partitions)
def do(data, resource):
    body = {}
    params = data['params']

    # 파티션
    current_partitions = resource.fdb_get_partitions(use_cache=False)
    body['partitions'] = current_partitions
    return body
