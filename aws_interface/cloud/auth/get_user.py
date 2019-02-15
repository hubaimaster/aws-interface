from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_id': 'str'
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'group': 'str',
            'extra': 'map',
        }
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    user_id = params.get('user_id', None)

    table_name = 'auth-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    result = dynamo.get_item(table_name, user_id)
    item = result.get('Item', None)
    body['item'] = item
    return Response(body)
