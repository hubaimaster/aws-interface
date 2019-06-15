def has_permission(user, item):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, 'read_groups': [str], 'write_groups': [str], ..+}
    :return: bool, determines if user has permission to update an item.
    """
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
