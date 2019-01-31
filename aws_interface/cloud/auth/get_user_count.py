from cloud.aws import *


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    app_id = data['app_id']

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    partition = 'user'

    dynamo = DynamoDB(boto3)
    count = dynamo.get_item_count(table_name, '{}-count'.format(partition))
    item = count.get('Item', {'count': 0})
    response['item'] = item
    return response
