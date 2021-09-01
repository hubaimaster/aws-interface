def has_permission(user, item):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, ..+}
    :return: bool, determines if user has permission to delete an item.
    """
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    user_id = user.get('id', None)
    if 'admin' in user_groups:
        return True
    if user_id == item.get('owner', None):
        return True
    return False
