from cloud.aws import *


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
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_group = user.get('group', None)
    item_id = params.get('item_id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)

    item = dynamo.get_item(table_name, item_id)
    read_permission = item.get('Item', {}).get('read_permissions', [])
    if 'all' in read_permission or user_group in read_permission:
        # Remove system key
        item.get('Item', {}).pop('partition', None)
        item.get('Item', {}).pop('read_permissions', None)
        item.get('Item', {}).pop('write_permissions', None)
        response['item'] = item
        response['success'] = True
    else:
        response['success'] = False
        response['message'] = 'permission denied'
    return response
