
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'memory_size': 'int',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Set function global meta data [EX: memory, ...]'
}


@NeedPermission(Permission.Run.Logic.set_function_metadata)
def do(data, resource):
    body = {}
    params = data['params']

    updated_metadata_list = []

    memory_size = params.get('memory_size', None)
    if memory_size:
        resource.function_update_memory_size(memory_size)
        updated_metadata_list.append('memory_size')

    body['updated_metadata_list'] = updated_metadata_list
    body['success'] = True
    return body
