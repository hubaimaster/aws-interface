from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str'
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

    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)

    table_name = 'auth-{}'.format(app_id)
    partition = 'session'

    dynamo = DynamoDB(boto3)
    result = dynamo.get_items(table_name, partition, exclusive_start_key=start_key, limit=limit)
    items = result.get('Items', [])
    end_key = result.get('LastEvaluatedKey', None)
    body['items'] = items
    body['end_key'] = end_key
    return Response(body)
