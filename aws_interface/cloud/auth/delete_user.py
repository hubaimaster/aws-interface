from cloud.aws import *
import boto3


def do(data):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    _user_id = params.get('id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    result = dynamo.delete_item(table_name, _user_id)
    response['success'] = True
    return response
