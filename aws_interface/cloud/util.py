def has_read_permission(user, item):
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    groups = item.get('read_groups', [])

    for user_group in user_groups:
        if user_group in groups or user_group == 'admin':
            return True
        elif 'owner' in groups and user_id == item.get('owner'):
            return True
        return False


def has_write_permission(user, item):
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    groups = item.get('write_groups', [])

    for user_group in user_groups:
        if user_group in groups or user_group == 'admin':
            return True
        elif 'owner' in groups and user_id == item.get('owner'):
            return True
        return False


def has_run_permission(user, item):
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    groups = item.get('run_groups', [])

    for user_group in user_groups:
        if user_group in groups or user_group == 'admin':
            return True
        elif 'owner' in groups and user_id == item.get('owner'):
            return True
        return False


system_partitions = ['user', 'log']


def database_can_not_access_to_item(item):
    partition = item.get('partition', None)
    if not partition:
        return True
    if partition in system_partitions:
        return True
    else:
        return False
