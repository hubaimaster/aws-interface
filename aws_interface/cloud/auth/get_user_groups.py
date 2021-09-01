
from cloud.permission import Permission
import time


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'groups': [{'str': 'any'}],
    },
    'description': 'Return all groups enrolled in system'
}

# 자주 읽는데 용량이 커서 분 단위 캐싱
cache = {}


def get_cache(key):
    if key in cache:
        return cache[key]
    return None


def set_cache(key, value):
    cache[key] = value


def do(data, resource):
    now = time.time()
    key = int(now / 10)
    body = get_cache(key)
    if body:
        return body
    body = {}

    default_groups = {
        'user': {
            'name': 'user',
            'description': 'Default user group',
            'permissions': Permission.default_user_permissions,
        },
        'unknown': {
            'name': 'unknown',
            'description': 'For not signed in user',
            'permissions': Permission.unknown_user_permissions,
        }
    }
    admin_groups = {
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

    group_items = [group_item for group_item in group_items if group_item['name'] not in admin_groups]
    group_items = list(group_items)
    for group_name in admin_groups:
        group = admin_groups[group_name]
        group_items.append(group)

    body['groups'] = group_items
    set_cache(key, body)
    return body
