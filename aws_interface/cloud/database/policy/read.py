def has_permission(user, item):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, 'read_groups': [str], 'write_groups': [str], ..+}
    :return: bool, determines if user has permission to read an item.
    """
    return True
