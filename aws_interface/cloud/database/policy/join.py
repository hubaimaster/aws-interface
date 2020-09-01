def has_permission(user, join):
    """
    :param user: {'id': str, 'creation_date': float, 'groups': [str], 'email': str, ..}
    :param join: {'item_id_to_join': 'item_to_be_joined', ..}
    :return: bool, determines if user has permission to join an item.
    You can also modify join by ref. like this: join["<some_item_id>"] = "<target_field>"
    """
    return True
