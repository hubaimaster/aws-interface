
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from uuid import uuid4

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'slack_webhook_name': 'str',
    },
    'output_format': {
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Set slack webhook for system notification. (Such as error notice..)'
}


@NeedPermission(Permission.Run.Notification.create_system_notification)
def do(data, resource):
    body = {}
    params = data['params']

    slack_webhook_name = params.get('slack_webhook_name')

    query = [{
        'condition': 'eq',
        'field': 'name',
        'value': slack_webhook_name,
        'option': None
    }]
    items, _ = resource.db_query('slack_webhook', query)
    if items:
        item = items[0]
        item_id = item.get('id')
        name = item.get('name')
        success = resource.db_put_item('system_notification', {
            'slack_webhook_id': item_id,
            'slack_webhook_name': name
        })
        body['success'] = success
    else:
        body['error'] = error.NO_SUCH_SLACK_WEBHOOK
        body['success'] = False

    return body
