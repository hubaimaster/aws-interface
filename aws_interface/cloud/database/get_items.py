from cloud.aws import *
from cloud.response import Response
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'start_key': 'dict',
        'limit': 'int=100',
        'reverse': 'bool=False',
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str'
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_group = user.get('group', None)
    partition = params.get('partition', None)
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    if type(start_key) is str:
        start_key = json.loads(start_key)

    table_name = 'database-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    result = dynamo.get_items(table_name, partition, start_key, limit, reverse)
    end_key = result.get('LastEvaluatedKey', None)
    items = result.get('Items', [])

    filtered = []
    for item in items:
        read_permission = item.get('read_groups', [])
        if 'all' in read_permission or user_group in read_permission:
            # Remove system key
            item.pop('partition', None)
            item.pop('read_groups', None)
            item.pop('write_groups', None)
            filtered.append(item)

        body['items'] = filtered
    body['end_key'] = end_key
    return Response(body)
