
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'start_key': 'str?',
    },
    'output_format': {
        'items': [
            {
                'name': 'str',
                'description': 'str',
            }
        ],
        'email_providers_end_key': 'str?',
    },
    'description': 'Return webhook info'
}


@NeedPermission(Permission.Run.Logic.get_webhooks)
def do(data, resource):
    body = {}
    params = data['params']
    start_key = params.get('start_key', None)

    items, end_key = resource.db_get_items_in_partition('webhook', start_key=start_key)
    body['items'] = items
    body['email_providers_end_key'] = end_key
    return body
