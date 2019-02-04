from cloud.aws import *


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'start_key': 'str',
        'limit': 'int=100'
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
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)

    result = dynamo.get_items(table_name, partition, start_key, limit)
    end_key = result.get('LastEvaluatedKey', None)
    items = result.get('Items', [])

    filtered = []
    for item in items:
        read_permission = item.get('read_permissions', [])
        if 'all' in read_permission or user_group in read_permission:
            filtered.append(item)

    response['items'] = filtered
    response['end_key'] =  end_key
    return response
