from concurrent.futures import ThreadPoolExecutor
from cloud.database.get_policy_code import get_policy_code, match_policy


def _get_joined_item_id(item, key, joined_item_ids=[]):
    if key.startswith('.') or key.endswith('.'):
        raise Exception('Invalid join key error: {}'.format(key))
    if '.' in key:
        keys = key.split('.')
        item = item.get(keys[0], None)
        if item:
            return _get_joined_item_id(item, '.'.join(keys[1:]), joined_item_ids)
        return None
    return item.get(key, None)


def _put_joined_item(item, target, joined_item):
    if target.startswith('.') or target.endswith('.'):
        raise Exception('Invalid join target error: {}'.format(target))
    if '.' in target:
        targets = target.split('.')
        return _put_joined_item(item[targets[0]], '.'.join(targets[1:]), joined_item)
    item[target] = joined_item


def join_item(resource, user, item, join, policy_code_cache={}):
    """
    item 에서 join 할 항목을 찾아 join 하고 반환합니다.
    :param resource:
    :param user:
    :param item:
    :param join: {'item_id': 'item',
                  'info.user_id': 'info.user',
                  'info.user_id': 'user'}
    :param policy_code_cache:
    :return:
    """

    with ThreadPoolExecutor(max_workers=min(len(join), 16)) as ex:
        for _key, _target in join.items():
            def work_join(key, target):
                joined_item_id = _get_joined_item_id(item, key)
                if joined_item_id:
                    joined_item = resource.db_get_item(joined_item_id)
                    if joined_item:
                        partition = joined_item.get('partition')
                        if partition in policy_code_cache:
                            policy_code = policy_code_cache[partition]
                        else:
                            policy_code = get_policy_code(resource, partition, 'read')
                            policy_code_cache[partition] = policy_code
                        if match_policy(policy_code, user, joined_item):
                            _put_joined_item(item, target, joined_item)
            ex.submit(work_join, _key, _target)
    return item


def join_items(resource, user, items, join):
    policy_code_cache = {}
    joined_item_ids = []
    joined_item_pairs = {}

    for item in items:
        for key, target in join.items():
            joined_item_id = _get_joined_item_id(item, key)
            if joined_item_id:
                joined_item_ids.append(joined_item_id)

    joined_item_ids = list(set(joined_item_ids))

    bulk_size = 100
    with ThreadPoolExecutor(max_workers=10) as exc1:
        for i in range(0, len(joined_item_ids), bulk_size):
            def get_bulk(start, end):
                joined_items = resource.db_get_items(joined_item_ids[start:end])
                for _joined_item in joined_items:
                    joined_item_pairs[_joined_item['id']] = _joined_item
            exc1.submit(get_bulk, i, i + bulk_size)

    with ThreadPoolExecutor(max_workers=100) as exc2:
        for _item in items:
            for _key, _target in join.items():
                def work_join(item_, key_, target_):
                    joined_item_id_ = _get_joined_item_id(item_, key_)
                    if joined_item_id_:
                        joined_item = joined_item_pairs[joined_item_id_]

                        if joined_item:
                            partition = joined_item.get('partition')
                            if partition in policy_code_cache:
                                policy_code = policy_code_cache[partition]
                            else:
                                policy_code = get_policy_code(resource, partition, 'read')
                                policy_code_cache[partition] = policy_code
                            if match_policy(policy_code, user, joined_item):
                                _put_joined_item(item_, target_, joined_item)
                exc2.submit(work_join, _item, _key, _target)
