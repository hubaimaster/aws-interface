
from cloud.permission import Permission, NeedPermission
from cloud.message import error


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'name': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Return webhook info'
}


@NeedPermission(Permission.Run.Logic.get_webhook)
def do(data, resource):
    body = {}
    params = data['params']
    name = params.get('name')

    item_id = 'webhook-{}'.format(name)
    webhook = resource.db_get_item(item_id)
    if webhook:
        body['webhook'] = webhook
        return body
    else:
        body['error'] = error.NO_SUCH_WEBHOOK
        return body
