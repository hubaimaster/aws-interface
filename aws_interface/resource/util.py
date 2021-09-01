from resource.config import MAX_N_GRAM


def has_sub_tuple(tuple_list, sub_tuple):
    """
    리스트에 부분 튜플이 있는지 확인
    :param tuple_list
    :param sub_tuple:
    :return:
    """
    has = False
    for tup in tuple_list:
        if len(sub_tuple) <= len(tup):
            sub = True
            for idx, element in enumerate(sub_tuple):
                if tup[idx] != element:
                    sub = False
            if sub:
                has = True
    return has


def is_sub_tuple(tup, sub_tuple):
    if isinstance(tup, tuple) and isinstance(sub_tuple, tuple):
        if len(sub_tuple) <= len(tup):
            sub = True
            for idx, element in enumerate(sub_tuple):
                if tup[idx] != element:
                    sub = False
            return sub
    return False


def get_item(tup, index, defaultvalue=None):
    if len(tup) > index:
        return tup[index]
    return defaultvalue


def find_ins_n_gram(index_keys, field):
    """
    ins 연산자의 n_gram 토큰 개수를 찾습니다.
    :param index_keys:
    :param field:
    :return:
    """
    if index_keys:
        for index_key in index_keys:
            if is_sub_tuple(index_key, (field, 'ins')):
                return get_item(index_key, 2, MAX_N_GRAM)
    return MAX_N_GRAM
