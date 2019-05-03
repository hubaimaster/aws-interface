def has_read_permission(user, item):
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    groups = item.get('read_groups', [])
    groups.append('admin')
    for user_group in user_groups:
        if user_group in groups:
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
    groups.append('admin')
    for user_group in user_groups:
        if user_group in groups:
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
    groups.append('admin')
    for user_group in user_groups:
        if user_group in groups:
            return True
        elif 'owner' in groups and user_id == item.get('owner'):
            return True
        return False
