def has_permission(user, _):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param _: Void
    :return: bool, determines if system has permission to write index for a database row item.
    For example, if you want to index 'name' and 'phone', You should write like bellow.
    --- ex ---
    return ['name', 'phone']
    --- Or if you want to index all keys ---
    return True
    ___ Or if you do not want to index
    return []
    """
    return True
