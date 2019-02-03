from cloud.aws import *


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'start_key': 'str',
        'limit': 'int'
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str'
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_group = user.get('group', None)
    partition = params.get('partition', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)

    items = dynamo.get_items(table_name, partition)
    for item in items:  # Problem of efficiency TODO TODO TODO TODO TODO !!!
        read_permission = item.get('Item', {}).get('read_permissions', [])
        if 'all' in read_permission or user_group in read_permission:
            response['item'] = item
            response['success'] = True
        else:
            response['success'] = False
            response['message'] = 'permission denied'
        return response