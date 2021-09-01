def has_permission(user, item):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, ..+}
    :return: bool, determines if user has permission to read an item.
    You can also modify item by ref. like this: item['field'] = 'value'
    """
    return True
