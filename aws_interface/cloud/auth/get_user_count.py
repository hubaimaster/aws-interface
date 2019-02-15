from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'item': {
            'count': 'int'
        }
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    app_id = data['app_id']

    table_name = 'auth-{}'.format(app_id)
    partition = 'user'

    dynamo = DynamoDB(boto3)
    count = dynamo.get_item_count(table_name, '{}-count'.format(partition))
    item = count.get('Item', {'count': 0})
    body['item'] = item
    return Response(body)
