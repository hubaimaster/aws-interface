
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'path': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    user_id = user.get('id', None)

    def has_permission(_item):
        write_groups = _item['write_groups']
        if 'owner' in write_groups:
            owner_id = _item['owner']
            if owner_id == user_id:
                return True
        user_group = user['group']
        return user_group in write_groups

    _path = params.get('path')
    item = resource.db_get_item(_path)

    def delete_item(_item):
        if has_permission(_item):
            resource.db_delete_item(_path)
            file_key = item.get('file_key', None)
            if file_key:
                resource.file_delete_base64(file_key)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)

    if item:
        delete_item(item)
        body['success'] = True
        return Response(body)
    else:
        body['success'] = False
        body['message'] = 'folder_path: {} does not exist'.format(_path)
        return Response(body)

