def has_permission(user, index_keys):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param index_keys: ['id', 'creation_date', 'name', 'phone', ...]
    :return: index_keys:[str], determines if system has permission to write index for a database row item.
    For example, if you want to index 'name' and 'phone', You should write like bellow.
    --- ex ---
    return ['name', 'phone']
    --- Or if you want to index all keys ---
    return index_keys
    """
    return index_keys
