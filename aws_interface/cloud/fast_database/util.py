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
