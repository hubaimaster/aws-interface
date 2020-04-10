
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
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Create slack webhook.'
}


@NeedPermission(Permission.Run.Notification.get_slack_webhooks)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    start_key = params.get('start_key', None)

    items, end_key = resource.db_query('slack_webhook', start_key=start_key)
    body['items'] = items
    body['end_key'] = end_key

    return body
