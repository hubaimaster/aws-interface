def has_permission(user, item):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, ..+}
    :return: bool, determines if user has permission to delete an item.
    """
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    if 'admin' in user_groups:
        return True
    return False
