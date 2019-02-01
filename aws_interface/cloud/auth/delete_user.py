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

    user_id = params.get('user_id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    _ = dynamo.delete_item(table_name, 'user', user_id)
    response['success'] = True
    return response
