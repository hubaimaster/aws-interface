from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'folder_path': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_id = user.get('id', None)

    def has_permission(_item):
        read_groups = _item['read_groups']
        if 'owner' in read_groups:
            owner_id = _item['owner']
            if owner_id == user_id:
                return True
        user_group = user['group']
        return user_group in read_groups

    folder_path = params.get('folder_path')

    table_name = 'storage-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    item = dynamo.get_item(table_name, folder_path).get('Item')
    if item:
        if has_permission(item):
            if item['type'] == 'folder':
                # TODO Should remove files recursively..
                dynamo.delete_item(table_name, folder_path)
                body['success'] = True
                return Response(body)
            else:
                body['success'] = False
                body['message'] = 'file_path is not a file'
                return Response(body)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'folder_path: {} does not exist'.format(folder_path)
        return Response(body)

