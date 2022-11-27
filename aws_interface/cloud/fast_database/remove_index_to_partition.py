
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'index_name': 'str',
    },
    'output_format': {
        'partition': 'str',
        'result': 'dict',
    },
    'description': 'Remove index to partition and return partition name'
}


@NeedPermission(Permission.Run.FastDatabase.remove_index_to_partition)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params.get('partition', None)
    index_name = params.get('index_name', None)

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION
    if not index_name:
        raise errorlist.NEED_INDEX_NAME

    if has_partition(resource, partition, use_cache=False):
        raise errorlist.EXISTING_PARTITION

    result = resource.fdb_detach_index(partition, index_name)
    body['partition'] = partition
    body['result'] = result
    return body
