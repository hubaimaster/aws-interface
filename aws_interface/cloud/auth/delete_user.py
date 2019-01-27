from cloud.aws import *
import boto3


def do(data):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    user_id = params.get('user_id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    _ = dynamo.delete_item(table_name, 'user', user_id)
    response['success'] = True
    return response
