
from cloud.response import Response
from cloud.util import has_read_permission
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_key': 'str',
    },
    'output_format': {
        'file_b64': 'str',
        'success': 'bool'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_key = params.get('file_key')

    item = resource.db_get_item(file_key)
    if item:
        if has_read_permission(user, item):
            file_key = item['file_key']
            file_b64 = resource.file_download_base64(file_key)
            body['file_b64'] = file_b64
            body['success'] = True
            return Response(body)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'file_key: {} does not exist'.format(file_key)
        return Response(body)

