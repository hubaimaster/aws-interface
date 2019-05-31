def has_permission(user, item):
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
