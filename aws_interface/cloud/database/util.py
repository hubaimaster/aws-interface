def has_read_permission(user, item):
    group = user.get('group', None)
    user_id = user.get('id', None)
    groups = item.get('read_groups', [])
    if group in groups:
        return True
    elif 'owner' in groups and user_id == item.get('owner'):
        return True
    return False


def has_write_permission(user, item):
    group = user.get('group', None)
    user_id = user.get('id', None)
    groups = item.get('write_groups', [])
    if group in groups:
        return True
    elif 'owner' in groups and user_id == item.get('owner'):
        return True
    return False
