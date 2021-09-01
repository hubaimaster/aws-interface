
from cloud.storage.get_policy_code import match_policy_after_get_policy_code
from cloud.permission import Permission, NeedPermission
from cloud.message import error
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_id': 'str',
        'use_plain?': 'bool=false',
    },
    'output_format': {
        'file_b64': 'str',
        'parent_file_id?': 'str',
        'file_name?': 'str',
        'meta_info': {
            '...': '...'
        }
    },
    'description': 'Download a file chunk as base64 encoding'
}


@NeedPermission(Permission.Run.Storage.download_b64)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    file_id = params.get('file_id')
    use_plain = params.get('use_plain', False)

    if not file_id:
        body['error'] = error.INVALID_FILE_KEY
        return body

    item = resource.db_get_item(file_id)
    if item:
        if match_policy_after_get_policy_code(resource, 'read', 'files', user, item):
            file_id = item['file_id']
            parent_file_id = item.get('parent_file_id', None)
            file_b64 = resource.file_download_bin(file_id)
            if not use_plain:
                file_b64 = base64.b64encode(file_b64)
            file_b64 = file_b64.decode('utf-8')

            body['file_b64'] = file_b64
            body['parent_file_id'] = parent_file_id
            body['file_name'] = item.get('file_name', None)
            body['meta_info'] = item.get('meta_info', {})
            return body
        else:
            body['error'] = error.PERMISSION_DENIED
            return body
    else:
        body['error'] = error.INVALID_FILE_KEY
        return body
