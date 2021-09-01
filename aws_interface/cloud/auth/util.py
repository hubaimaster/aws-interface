
cache = {}


def set_cache(item_id, item):
    cache[item_id] = item


def get_cache(item_id):
    item = cache.get(item_id, None)
    return item


def already_has_account_email(email, resource):
    items, _ = resource.db_query('user', [
        (None, ('email', 'eq', email)),
    ])
    if items:
        return True
    else:
        return False


def simplify_item(item, new_item):
    """
    new_item 에서 item 에 이미 있는 동일 항목을 제외하여 반환합니다.
    :param item:
    :param new_item:
    :return:
    """
    simple_items = {key: value for key, value in new_item.items() if value != item.get(key, None)}
    return simple_items

