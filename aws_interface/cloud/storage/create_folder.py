from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'parent_path': 'str',
        'folder_name': 'str',
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'success': 'bool'
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_id = user.get('id', None)

    parent_path = params.get('parent_path')
    folder_name = params.get('folder_name')
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    folder_path = str(parent_path)
    if not folder_path.endswith('/'):
        folder_path += '/'
        folder_path += folder_name

    item = {
        'owner': user_id,
        'parent_path': parent_path,
        'folder_name': folder_name,
        'read_groups': read_groups,
        'write_groups': write_groups,
        'folder_path': folder_path,
    }
    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)

    folder = dynamo.get_item(table_name, folder_path)
    if folder.get('Item'):
        body['success'] = False
        return Response(body)

    dynamo.put_item(table_name, 'folder', item, item_id=folder_path)
    body['success'] = True
    return Response(body)
