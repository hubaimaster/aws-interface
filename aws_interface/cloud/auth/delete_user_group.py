
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str'
    },
    'output_format': {
        'items': 'list',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    name = params['name']

    item = resource.db_get_item('user_groups')
    if not item:
        item = {}

    groups = item.get('groups', {})
    if name in groups:
        groups.pop(name)
    body['groups'] = groups
    resource.db_put_item('meta-info', item, 'user_groups')
    return Response(body)
