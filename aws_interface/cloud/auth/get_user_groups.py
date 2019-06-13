
from cloud.response import Response
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'groups': [{'str': 'any'}],
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    default_groups = {
        'user': {
            'name': 'user',
            'description': 'Default user group',
            'permissions': Permission.default_user_permissions,
        },
        'admin': {
            'name': 'admin',
            'description': 'Admin has full control of the system',
            'permissions': Permission.all(),
        }
    }

    group_items, _ = resource.db_get_items_in_partition('user_group', limit=10000)
    has_default_groups = True
    for group_name in default_groups:
        if group_name not in [group_item['name'] for group_item in group_items]:
            has_default_groups = False
            resource.db_put_item('user_group', default_groups[group_name], 'user-group-{}'.format(group_name))

    if not has_default_groups:
        group_items, _ = resource.db_get_items_in_partition('user_group', limit=10000)

    body['groups'] = group_items
    return Response(body)
