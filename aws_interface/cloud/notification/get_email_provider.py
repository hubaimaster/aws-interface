
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Get email provider info by name'
}


@NeedPermission(Permission.Run.Notification.delete_email_provider)
def do(data, resource):
    body = {}
    params = data['params']

    name = params.get('name')

    inst = [
        {'field': 'name', 'value': name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('email_provider', inst)
    if items:
        item = items[0]
        body['item'] = item
        return body
    else:
        body['error'] = error.NO_SUCH_EMAIL_PROVIDER
        return body
