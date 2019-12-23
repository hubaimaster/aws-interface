
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str',
        'description': 'str?',
        'url': 'str',
        'port': 'int',
        'email': 'str',
        'password': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Create email provider info. The system can send email via this provider.'
}


@NeedPermission(Permission.Run.Notification.create_email_provider)
def do(data, resource):
    body = {}
    params = data['params']

    name = params.get('name')
    description = params.get('description', None)
    url = params.get('url')
    port = params.get('port')
    email = params.get('email')
    password = params.get('password')

    email_provider = {
        'name': name,
        'description': description,
        'url': url,
        'port': port,
        'email': email,
        'password': password
    }

    inst = [
        {'field': 'name', 'value': name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('email_provider', inst)
    if items:
        body['error'] = error.EXISTING_EMAIL_PROVIDER
        return body

    success = resource.db_put_item('email_provider', email_provider)
    body['success'] = success
    return body
