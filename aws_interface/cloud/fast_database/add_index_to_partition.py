
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'pk_field': 'str',
        'sk_field': 'str',
    },
    'output_format': {
        'partition': 'str',
        'result': 'dict',
    },
    'description': 'Add index to partition and return partition name'
}


@NeedPermission(Permission.Run.FastDatabase.add_index_to_partition)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params.get('partition', None)
    pk_field = params.get('pk_field', None)
    sk_field = params.get('sk_field', None)

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION
    if not pk_field:
        raise errorlist.NEED_PK_FIELD
    if not sk_field:
        raise errorlist.NEED_SK_FIELD

    if not has_partition(resource, partition, use_cache=False):
        raise errorlist.NO_SUCH_PARTITION

    result = resource.fdb_append_index(partition, pk_field, sk_field)
    body['partition'] = partition
    body['result'] = result
    return body
