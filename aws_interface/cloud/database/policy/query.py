def has_permission(user, query):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..+}
    :param query: [{'condition': 'eq' | 'neq' | 'in' | 'nin' | 'gt' | 'ge' | 'ls' | 'le',
                    'option': 'or' | 'and' | None,
                    'field': 'str',
                    'value': 'object'}]
    :return: bool, determines if user has permission to query an item.
    You can also modify query by ref. like this: query.append({'condition': 'eq', ...})
    """
    return True
