def has_permission(user, user_to_update):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param user_to_update: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :return: bool, determines if user has permission to update an item.
    You can also modify item by ref. like this: item['field'] = 'value'
    """
    return True
