
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str?'
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Get all email providers.'
}


@NeedPermission(Permission.Run.Notification.get_email_providers)
def do(data, resource):
    body = {}
    params = data['params']

    start_key = params.get('start_key', None)

    inst = []
    items, end_key = resource.db_get_items_in_partition('email_provider', start_key=start_key)
    body['items'] = items
    body['end_key'] = end_key
    return body
