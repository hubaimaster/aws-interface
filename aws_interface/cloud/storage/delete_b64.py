
from cloud.response import Response
from cloud.util import has_write_permission
# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_key': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_key = params.get('file_key')
    item = resource.db_get_item(file_key)

    if item:
        if has_write_permission(user, item):
            resource.db_delete_item(file_key)
            file_key = item.get('file_key', None)
            if file_key:
                resource.file_delete_base64(file_key)
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

