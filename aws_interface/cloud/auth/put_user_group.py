
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'name': 'str'
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    name = params['name']
    description = params['description']
    if not description:
        description = None

    item = resource.db_get_item('user_groups')
    if not item:
        item = {}

    groups = item.get('groups', {})
    groups[name] = {
        'name': name,
        'description': description,
    }

    item['groups'] = groups
    resource.db_put_item('meta-info', item, 'user_groups')

    body['success'] = True
    return Response(body)
