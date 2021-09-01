def has_permission(user, user_to_read):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param user_to_read: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :return: bool, determines if user has permission to read an item.
    You can also modify item by ref. like this: item['field'] = 'value'
    """
    return True
