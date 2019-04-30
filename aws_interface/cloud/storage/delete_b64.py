
from cloud.response import Response
from cloud.util import has_write_permission
# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'message': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_id_to_delete = params.get('file_id')

    while file_id_to_delete:
        file_item = resource.db_get_item(file_id_to_delete)
        if file_item and has_write_permission(user, file_item):
            resource.file_delete_bin(file_id_to_delete)
            resource.db_delete_item(file_id_to_delete)

            file_id_to_delete = file_item.get('parent_file_id', None)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)

    body['success'] = True
    return Response(body)
