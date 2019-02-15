from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'path': 'str',
        'start_key': 'str?',
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str',
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
    start_key = params.get('start_key', None)

    table_name = 'storage-{}'.format(app_id)
    dynamo = DynamoDB(boto3)

    item = dynamo.get_item(table_name, folder_path).get('Item', None)
    if item:
        if has_permission(item):
            result = dynamo.get_items(table_name, folder_path, start_key)
            body['items'] = result.get('Items', [])
            body['end_key'] = result.get('LastEvaluatedKey', None)
            return Response(body)
        else:
            body['success'] = False
            body['message'] = 'Permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'No folder_path: {}'.format(folder_path)
        return Response(body)

