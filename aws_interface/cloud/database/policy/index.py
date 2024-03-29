def has_permission(user, _):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param _: Void
    :return: bool, determines if system has permission to write index for a database row item.
    For example, if you want to index 'name' and 'phone', You should write like bellow.
    --- ex ---
    return ['<field>', '<field2>']
    --- Or if you want to index all keys ---
    return True
    ___ Or if you do not want to index
    return []
    ___ Or if you want to index full-text
    return ['<field>', ('<field_want_to_index>', 'ins')]
    --- Case of separating Read/Write index (Read as first element, Write as second element in tuple)
    return ['<field>', '<field2>'], True
    """
    return True
