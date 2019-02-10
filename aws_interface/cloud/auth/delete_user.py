from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
    },
    'output_format': {
        'success': 'bool'
    }
}


def do(data, boto3):
    body = {
        'status'
    }
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    user_id = params.get('user_id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    _ = dynamo.delete_item(table_name, user_id)
    body['success'] = True
    return Response(body)
