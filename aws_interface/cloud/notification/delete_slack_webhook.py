
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from uuid import uuid4

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str',
    },
    'output_format': {
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Create slack webhook.'
}


@NeedPermission(Permission.Run.Notification.delete_slack_webhook)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    name = params.get('name')

    query = [{
        'condition': 'eq',
        'field': 'name',
        'value': name,
        'option': None
    }]
    items, _ = resource.db_query('slack_webhook', query)
    if items:
        item = items[0]
        item_id = item.get('id')
        success = resource.db_delete_item(item_id)
        body['success'] = success
    else:
        body['error'] = error.NO_SUCH_SLACK_WEBHOOK
        body['success'] = False

    return body
