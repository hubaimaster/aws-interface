
from cloud.response import Response
import cloud.shortuuid as shortuuid
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'parent_path': 'str',
        'index': 'int',
        'size': 'int',
        'file_b64': 'str',
        'file_name': 'str',
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'success': 'bool'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_id = user.get('id', None)

    index = params.get('index')
    size = params.get('size')
    file_b64 = params.get('file_b64')
    file_name = params.get('file_name')
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    file_bin = base64.b64decode(file_b64)

    split_file_name = '{}_{}'.format(file_name, index)

    parent_path = 'dummy'
    file_path = str(parent_path)
    if not file_path.endswith('/'):
        file_path += '/'
    file_path += split_file_name

    file_key = '{}-{}'.format(shortuuid.uuid(), split_file_name)

    resource.file_upload_base64(file_key, file_bin)

    item = {
        'owner': user_id,
        'parent_path': parent_path,
        'name': file_name,
        'path': file_path,
        'file_key': file_key,
        'index': index,
        'size': size,
        'read_groups': read_groups,
        'write_groups': write_groups,
        'type': 'split_file',
    }
    print(item)

    resource.db_put_item('storage-files', item, file_path)
    body['success'] = True
    return Response(body)
