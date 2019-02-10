from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'item': 'map',
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_group = user.get('group', None)
    item_id = params.get('item_id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)

    item = dynamo.get_item(table_name, item_id)
    item = item.get('Item', {})
    read_permission = item.get('read_permissions', [])
    if 'all' in read_permission or user_group in read_permission:
        # Remove system key
        item.pop('partition', None)
        item.pop('read_permissions', None)
        item.pop('write_permissions', None)
        body['item'] = item
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
