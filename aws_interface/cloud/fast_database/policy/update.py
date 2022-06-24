def has_permission(user, item, new_item={}):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, ..+}
    :param new_item: {'id': str, 'creation_date': float, 'partition': str, 'owner': str, ..+}
    :return: bool, determines if user has permission to update an item.
    You can also modify item by ref. like this: item['field'] = 'value'
    """
    if user is None or item is None:
        return False
    user_groups = user.get('groups', [])
    if 'admin' in user_groups:
        return True
    return False
