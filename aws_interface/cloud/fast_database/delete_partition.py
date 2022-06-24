
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
    },
    'output_format': {
        'partition': 'str',
    },
    'description': 'Delete partition and return partition name'
}


@NeedPermission(Permission.Run.FastDatabase.delete_partition)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params.get('partition_name', None)

    # 파티션 없으면 에러
    if not has_partition(resource, partition, use_cache=False):
        raise errorlist.NO_SUCH_PARTITION

    result = resource.fdb_delete_partition(partition)
    body['partition_name'] = partition
    body['result'] = result
    return body
