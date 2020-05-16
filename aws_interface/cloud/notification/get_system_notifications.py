
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from uuid import uuid4

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str?',
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str'
    },
    'description': 'Get system notifications.'
}


@NeedPermission(Permission.Run.Notification.get_system_notifications)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    start_key = params.get('start_key', None)

    query = []
    items, end_key = resource.db_query('system_notification', query, start_key=start_key)
    body['items'] = items
    body['end_key'] = end_key

    return body
