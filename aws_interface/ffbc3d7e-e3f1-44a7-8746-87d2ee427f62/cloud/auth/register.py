from cloud.aws import *
import boto3
import uuid


def do(data):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    email = params['email']
    password = params['password']
    extra = params.get('extra', {})

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)  # Should be auth-143..
    dynamo = DynamoDB(boto3)

    item_id = str(uuid.uuid4())
    item = {
        'email': email,
        'password': password,
        'extra': extra,
    }
    dynamo.put_item(table_name, item_id, item)
    return response
