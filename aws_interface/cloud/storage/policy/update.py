def has_permission(user, item):
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    if 'admin' in user_groups:
        return True
    if user_id == item.get('owner', None):
        return True
    return False
