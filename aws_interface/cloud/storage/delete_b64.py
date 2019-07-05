from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.storage.get_policy_code import match_policy_after_get_policy_code
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_id': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Delete file entities'
}


@NeedPermission(Permission.Run.Storage.delete_b64)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_id_to_delete = params.get('file_id')

    while file_id_to_delete:
        file_item = resource.db_get_item(file_id_to_delete)

        if file_item and match_policy_after_get_policy_code(resource, 'delete', 'files', user, file_item):
            resource.file_delete_bin(file_id_to_delete)
            success = resource.db_delete_item(file_id_to_delete)
            body['success'] = success
            file_id_to_delete = file_item.get('parent_file_id', None)
        else:
            body['error'] = error.PERMISSION_DENIED
            return Response(body)

    return Response(body)
