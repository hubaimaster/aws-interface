
from cloud.permission import Permission, NeedPermission
from cloud.message import error


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'name': 'str',
        'description': 'str',
        'function_name': 'str',
    },
    'output_format': {
        'webhook': {
            'name': 'str',
            'description': 'str',
            'function_name': 'str',
        },
    },
    'description': 'Create webhook and return url to get access'
}


@NeedPermission(Permission.Run.Logic.create_webhook)
def do(data, resource):
    body = {}
    params = data['params']

    name = params.get('name')
    description = params.get('description', None)
    function_name = params.get('function_name')

    item_id = 'webhook-{}'.format(name)
    if resource.db_get_item(item_id):
        body['error'] = error.EXISTING_WEBHOOK
        return body
    else:
        webhook = {
            'name': name,
            'description': description,
            'function_name': function_name,
        }
        resource.db_put_item('webhook', webhook, item_id=item_id)
        body['webhook'] = webhook
        return body
