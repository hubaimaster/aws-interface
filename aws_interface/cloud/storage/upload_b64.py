import sys
from cloud.response import Response
from cloud.storage.get_policy_code import match_policy_after_get_policy_code
from cloud.permission import Permission, NeedPermission
from cloud.shortuuid import uuid
from cloud.message import error
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'parent_file_id?': 'str',
        'file_name?': 'str',
        'file_b64': 'str',

        'read_groups': 'list',
        'write_groups': 'list',

        'meta_info?': 'map',
    },
    'output_format': {
        'file_id': 'str',
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Storage.upload_b64)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    user_id = user.get('id', None)

    parent_file_id = params.get('parent_file_id', None)
    file_name = params.get('file_name', uuid())
    file_b64 = params.get('file_b64')

    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    meta_info = params.get('meta_info', {})

    file_id = '{}'.format(uuid())
    parent_file_info = None

    file_size = sys.getsizeof(file_b64)

    if parent_file_id:
        parent_file_info = resource.db_get_item(parent_file_id)
        if parent_file_info:
            if match_policy_after_get_policy_code(resource, 'create', 'files', user, parent_file_info):
                file_name = parent_file_info.get('file_name', None)
                parent_file_info['next_file_id'] = file_id
                file_size += parent_file_info['file_size']
            else:
                body['error'] = error.PERMISSION_DENIED
                return Response(body)

    file_info = {
        'file_id': file_id,
        'parent_file_id': parent_file_id,
        'file_name': file_name,
        'owner': user_id,
        'file_size': file_size,
        'read_groups': read_groups,
        'write_groups': write_groups,
        'meta_info': meta_info,
    }

    if match_policy_after_get_policy_code(resource, 'create', 'files', user, file_info):
        resource.db_put_item('files', file_info, file_id)
        if parent_file_id and parent_file_info:
            resource.db_update_item(parent_file_id, parent_file_info)

        file_b64 = file_b64.encode('utf-8')
        file_b64 = base64.b64decode(file_b64)
        resource.file_upload_bin(file_id, file_b64)

        body['file_id'] = file_id
        return Response(body)
    else:
        body['error'] = error.PERMISSION_DENIED
        return Response(body)

