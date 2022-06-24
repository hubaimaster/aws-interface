
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
    'description': 'Create partition and return partition name'
}


@NeedPermission(Permission.Run.FastDatabase.create_partition)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params.get('partition_name', None)
    pk_group = params.get('pk_group', None)
    pk_field = params.get('pk_field', None)
    sk_group = params.get('sk_group', None)
    sk_field = params.get('sk_field', None)
    post_sk_fields = params.get('post_sk_fields', [])
    use_random_sk_postfix = params.get('use_random_sk_postfix', True)

    if has_partition(resource, partition, use_cache=False):
        raise errorlist.EXISTING_PARTITION

    result = resource.fdb_create_partition(partition, pk_group, pk_field, sk_group, sk_field,
                                             post_sk_fields, use_random_sk_postfix)
    body['partition_name'] = partition
    body['result'] = result
    return body
