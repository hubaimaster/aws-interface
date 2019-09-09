
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
        'url': 'str'
    },
    'description': 'Return webhook info'
}


@NeedPermission(Permission.Run.Logic.get_webhook_url)
def do(data, resource):
    body = {}
    params = data['params']
    name = params.get('name')

    url = resource.create_webhook_url(name)
    body['url'] = url
    return body
