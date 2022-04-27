from concurrent.futures import ThreadPoolExecutor
from cloud.database.get_policy_code import get_policy_code, match_policy
import time

cache = {}


def get_sort_keys(resource):
    """
    sort_keys 를 가져옵니다.
    인덱스 생성에 함께 이용됩니다.
    :param resource:
    :param item:
    :return:
    """
    cache_key = f'sort_key_{int(time.time() / 10)}'
    if cache_key in cache:
        return cache[cache_key]
    sort_keys, _ = resource.db_query('sort_key', [], limit=10000)
    cache[cache_key] = sort_keys
    return sort_keys


def get_index_keys_to_index(resource, user, partition, mode):
    """
    인덱싱 할 키 목록 가져오기
    :param resource:
    :param user:
    :param partition:
    :param mode: 'r' | 'w' 읽기 / 쓰기
    :return:
    """
    policy_code = get_policy_code(resource, partition, 'index')
    index_keys = match_policy(policy_code, user, None)

    # 모드에 따라 인덱싱 키가 배정됨. 튜플일 경우만!
    if mode == 'r' and isinstance(index_keys, tuple) and len(index_keys) == 2:
        index_keys = index_keys[0]
    if mode == 'w' and isinstance(index_keys, tuple) and len(index_keys) == 2:
        index_keys = index_keys[1]

    if isinstance(index_keys, list):
        index_keys.extend(['partition'])
        index_keys = list(set(index_keys))
    return index_keys


def _get_joined_item_id(item, key):
    if key.startswith('.') or key.endswith('.'):
        raise Exception('Invalid join key error: {}'.format(key))
    if '.' in key:
        keys = key.split('.')
        item = item.get(keys[0], None)
        if item:
            return _get_joined_item_id(item, '.'.join(keys[1:]))
        return None
    if isinstance(item, dict):
        return item.get(key, None)
    else:
        return None


def _get_joined_item_ids(item, key):
    """
    Join Key 안에서 특정된 배열의 id 목록을 가져옵니다.
    :param item:
    :param key:
    :param joined_item_ids:
    :return:
    """
    if key.startswith('.') or key.endswith('.'):
        raise Exception('Invalid join key error: {}'.format(key))
    if '.' in key or key.endswith('[]'):
        keys = key.split('.')
        if keys[0].endswith('[]'):
            key_list = keys[0][:-2]
            items = item.get(key_list, [])
            item_ids = []
            for item in items:
                if item:
                    item_ids.append(_get_joined_item_ids(item, '.'.join(keys[1:])))
                else:
                    item_ids.append(None)
            return item_ids
        else:
            item = item.get(keys[0], None)
            if item:
                return _get_joined_item_ids(item, '.'.join(keys[1:]))
            return None
    if isinstance(item, dict):
        return item.get(key, None)
    elif isinstance(item, str):
        return item
    return None


def _put_joined_item(item, target, joined_item):
    if target.startswith('.') or target.endswith('.'):
        raise Exception('Invalid join target error: {}'.format(target))
    if '.' in target:
        targets = target.split('.')
        return _put_joined_item(item[targets[0]], '.'.join(targets[1:]), joined_item)
    item[target] = joined_item


def _put_joined_items(item, target, joined_items, idx=None):
    if target.startswith('.') or target.endswith('.'):
        raise Exception('Invalid join target error: {}'.format(target))
    if '.' in target or target.endswith('[]'):
        targets = target.split('.')
        if targets[0].endswith('[]'):
            target_list = targets[0][:-2]
            needs_idx = False
            if isinstance(item, dict):
                item.setdefault(target_list, [])
                if item[target_list]:
                    needs_idx = True
            elif isinstance(item, list):
                item.append([])
            for idx, joined_item in enumerate(joined_items):
                if isinstance(item, dict):
                    # item.setdefault(target_list, [])
                    if needs_idx:
                        _idx = idx
                    else:
                        _idx = None
                    _put_joined_items(item[target_list], '.'.join(targets[1:]), joined_item, _idx)
                elif isinstance(item, list):
                    # item.append([])
                    _put_joined_items(item[-1], '.'.join(targets[1:]), joined_item)
            return
        else:
            item.setdefault(targets[0], {})
            return _put_joined_items(item[targets[0]], '.'.join(targets[1:]), joined_items)
    if isinstance(item, list):
        if target:
            if idx is None:
                item.append({
                    target: joined_items
                })
            else:
                item[idx][target] = joined_items
        else:
            item.append(joined_items)
    else:
        item[target] = joined_items


def fetch_joined_items(resource, joined_item_ids, cache={}):
    """
    joined_item_ids 를 아이템 셋으로 변경합니다.
    :param resource:
    :param joined_item_ids:
    :param cache:
    :return:
    """
    futures = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        def fetch_work(joined_item_id):
            if isinstance(joined_item_id, list):
                _joined_items = fetch_joined_items(resource, joined_item_id, cache)
                return _joined_items
            elif cache.get(joined_item_id, None):
                return cache.get(joined_item_id)
            elif joined_item_id:
                item_ = resource.db_get_item(joined_item_id)
                cache[joined_item_id] = item_
                return item_
            else:
                return None
        for _joined_item_id in joined_item_ids:
            future = ex.submit(fetch_work, _joined_item_id)
            futures.append(future)
    return [future.result() for future in futures]


def validate_policy(resource, user, joined_items, policy_code_cache):
    for idx, joined_item in enumerate(joined_items):
        partition = joined_item.get('partition')
        if partition in policy_code_cache:
            policy_code = policy_code_cache[partition]
        else:
            policy_code = get_policy_code(resource, partition, 'read')
            policy_code_cache[partition] = policy_code
        if not match_policy(policy_code, user, joined_item):
            joined_items[idx] = None
    return joined_items


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

    def work_join(key, target):
        if '[]' in key:
            joined_item_ids = _get_joined_item_ids(item, key)
            if joined_item_ids:
                joined_items = fetch_joined_items(resource, joined_item_ids)
                joined_items = validate_policy(resource, user, joined_items, policy_code_cache)
                _put_joined_items(item, target, joined_items)
        else:
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

    with ThreadPoolExecutor(max_workers=min(len(join), 16)) as ex:
        for _key, _target in join.items():
            ex.submit(work_join, _key, _target)
    return item


def flatten(array_list):
    if array_list is None:
        return []
    flatted = []
    for elem in array_list:
        if isinstance(elem, list):
            flatted.extend(flatten(elem))
    return flatted


def join_items(resource, user, items, join):
    policy_code_cache = {}
    joined_item_ids = []
    joined_item_pairs = {}

    for _item in items:
        for key, target in join.items():
            if '[]' in key:
                _joined_item_ids = _get_joined_item_ids(_item, key)
                if _joined_item_ids:
                    _joined_item_ids = flatten(_joined_item_ids)
                    joined_item_ids.extend(_joined_item_ids)
            else:
                joined_item_id = _get_joined_item_id(_item, key)
                if joined_item_id and isinstance(joined_item_id, str):
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

    def work_join(item_, key_, target_):
        if '[]' in key_:
            joined_item_ids_ = _get_joined_item_ids(item_, key_)
            if joined_item_ids_:
                joined_items = fetch_joined_items(resource, joined_item_ids_, joined_item_pairs)
                joined_items = validate_policy(resource, user, joined_items, policy_code_cache)
                _put_joined_items(item_, target_, joined_items)
        else:
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

    with ThreadPoolExecutor(max_workers=100) as exc2:
        for _item in items:
            for _key, _target in join.items():
                exc2.submit(work_join, _item, _key, _target)


def simplify_item(item, new_item):
    """
    new_item 에서 item 에 이미 있는 동일 항목을 제외하여 반환합니다.
    :param item:
    :param new_item:
    :return:
    """
    simple_items = {key: value for key, value in new_item.items() if value != item.get(key, None)}
    return simple_items


if __name__ == '__main__':
    ids = _get_joined_item_ids({
        'a': [
            {'b': '1'},
            {'b': '2'},
            {'b': '3'},
        ]
    }, 'a[].b')
    print(ids)
    item = {}
    _put_joined_items(item, 'products[]', [{'id': '1'}, {'id': '2'}])
    print(item)