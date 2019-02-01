from cloud.aws import *

# Define the input output format of the function.
# This information is used when creating the *SDK*.
input_format = {

}
output_format = {
    'item': {
        'count': int
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    partition = 'session'

    dynamo = DynamoDB(boto3)
    result = dynamo.get_items(table_name, partition, exclusive_start_key=start_key, limit=limit)
    items = result.get('Items', [])
    end_key = result.get('LastEvaluatedKey', None)
    response['items'] = items
    response['end_key'] = end_key
    return response
