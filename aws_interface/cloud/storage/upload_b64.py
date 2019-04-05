
from cloud.response import Response
import cloud.shortuuid as shortuuid

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_b64': 'str',
        'file_name': 'str',
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'success': 'bool',
        'file_key': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    user_id = user.get('id', None)

    file_b64 = params.get('file_b64')
    file_name = params.get('file_name')
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    file_key = '{}-{}'.format(shortuuid.uuid(), file_name)

    resource.file_upload_base64(file_key, file_b64)

    item = {
        'owner': user_id,
        'name': file_name,
        'file_key': file_key,
        'read_groups': read_groups,
        'write_groups': write_groups,
    }
    resource.db_put_item('files', item, file_key)
    body['success'] = True
    return Response(body)
