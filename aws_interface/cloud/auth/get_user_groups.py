
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'groups': 'map',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    default_groups = {
        'user': {
            'name': 'user',
            'description': 'Normal user group',
        },
        # 'owner': {
        #     'name': 'owner',
        #     'description': 'Owner of file or object',
        # },
        # 'admin': {
        #     'name': 'admin',
        #     'description': 'Admin group',
        # },
    }

    item = resource.db_get_item('user_groups')
    if not item:
        item = {
            'groups': default_groups
        }
        resource.db_put_item('meta-info', item, 'user_groups')

    groups = item.get('groups')
    for group in default_groups:
        groups[group] = default_groups[group]

    body['groups'] = [groups[group] for group in groups]
    return Response(body)
