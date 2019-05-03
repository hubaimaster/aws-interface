
from cloud.response import Response
from cloud.util import has_read_permission
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'file_b64': 'str',
        'parent_file_id': 'str?',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_id = params.get('file_id')

    item = resource.db_get_item(file_id)
    if item:
        if has_read_permission(user, item):
            file_id = item['file_id']
            parent_file_id = item.get('parent_file_id', None)
            file_b64 = resource.file_download_bin(file_id)
            file_b64 = base64.b64encode(file_b64)
            file_b64 = file_b64.decode('utf-8')

            body['file_b64'] = file_b64
            body['parent_file_id'] = parent_file_id
            body['file_name'] = item.get('file_name', None)
            body['success'] = True
            return Response(body)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'file_key: {} does not exist'.format(file_id)
        return Response(body)

