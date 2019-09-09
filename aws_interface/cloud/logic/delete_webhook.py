
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
    'description': 'Delete webhook'
}


@NeedPermission(Permission.Run.Logic.delete_webhook)
def do(data, resource):
    body = {}
    params = data['params']

    name = params.get('name')

    item_id = 'webhook-{}'.format(name)
    success = resource.db_delete_item(item_id)
    body['success'] = success
    return body