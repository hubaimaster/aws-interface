
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str',

        'description': 'str?',
        'url': 'str?',
        'port': 'int?',
        'email': 'str?',
        'password': 'str?',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Update email provider info. The system can send email via this provider.'
}


@NeedPermission(Permission.Run.Notification.update_email_provider)
def do(data, resource):
    body = {}
    params = data['params']

    name = params.get('name')
    description = params.get('description', None)
    url = params.get('url', None)
    port = params.get('port', None)
    email = params.get('email', None)
    password = params.get('password', None)

    email_provider = {
        'name': name,
    }
    if description:
        email_provider['description'] = description
    if url:
        email_provider['url'] = url
    if port:
        email_provider['port'] = port
    if email:
        email_provider['email'] = email
    if password:
        email_provider['password'] = password

    inst = [
        {'field': 'name', 'value': name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('email_provider', inst)
    if items:
        item = items[0]
        success = resource.db_update_item(item.get('id'), email_provider)
        body['success'] = success
        return body
    else:
        body['error'] = error.NO_SUCH_EMAIL_PROVIDER
        return body
