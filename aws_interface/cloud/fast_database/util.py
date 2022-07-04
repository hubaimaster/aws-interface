"""
fdb 유틸리티
"""


def has_partition(resource, partition_name, use_cache=True):
    """
    시스템에 파티션이 존재하는지 확인, 캐시 사용 유무 체크할 수 있음. 파티션 삭제, 생성시엔 캐시 활용하면 안됨
    :param resource:
    :param partition_name:
    :param use_cache:
    :return:
    """

    # 파티션 존재하는지 체크
    current_partitions = resource.fdb_get_partitions(use_cache=use_cache)
    _has_partition = False
    for current_partition in current_partitions:
        _partition_name = current_partition.get('_partition_name', None)
        if _partition_name == partition_name:
            _has_partition = True
    return _has_partition


def valid_keys(item):
    """
    item 의 key 가 시스템에서 허용하는 것들인지
    예약 키일경우 거절
    :param item:
    :return:
    """
    for key, value in item.items():
        if key.startswith('_'):
            return False
    return True


def valid_pk_group(pk_group):
    """
    쿼리하는 pk_group 이 유효한지 확인
    :param pk_group:
    :return:
    """
    ban_list = [
        'meta-info'
    ]
    pk_group = str(pk_group)
    for ban in ban_list:
        if pk_group.startswith(ban):
            return False
    return True


def pop_ban_keys(item):
    """
    item 에서 _pk, _sk 등 시스템에서 보여줄 필요가 없는 것들을 pop
    :param item:
    :return:
    """
    if not item or not isinstance(item, dict):
        return item
    ban_keys = ['_pk', '_sk']
    item = item.copy()
    for ban_key in ban_keys:
        if ban_key in item:
            item.pop(ban_key)
    return item


if __name__ == '__main__':
    it = {
        'id': 'ooo',
        '_pk': 'ok',
        '_sk': 'ssa',
        'sid': 'aa'
    }
    it = pop_ban_keys(it)
    print(it)