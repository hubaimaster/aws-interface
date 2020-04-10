
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from uuid import uuid4

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str',
        'url': 'str',
    },
    'output_format': {
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Create slack webhook.'
}


@NeedPermission(Permission.Run.Notification.create_slack_webhook)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    name = params.get('name')
    url = params.get('url')
    item = {
        'name': name,
        'url': url,
    }
    query = [{
        'condition': 'eq',
        'field': 'name',
        'value': name,
        'option': None
    }]
    items, _ = resource.db_query('slack_webhook', query)
    if items:
        body['error'] = error.EXISTING_SLACK_WEBHOOK_NAME
        body['success'] = False
    else:
        success = resource.db_put_item('slack_webhook', item)
        body['success'] = success

    return body
