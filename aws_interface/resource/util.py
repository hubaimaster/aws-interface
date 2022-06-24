from resource.config import MAX_N_GRAM, BASE64_LETTERS


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


def divide_chunks(list_obj, n):
    # 입력된 리스트 l 을 n 개씩 갖도록 split
    # looping till length l
    if isinstance(list_obj, list):
        for i in range(0, len(list_obj), n):
            yield list_obj[i:i + n]
    elif isinstance(list_obj, dict):
        items = list(list_obj.items())
        for i in range(0, len(items), n):
            chunks = items[i: i+n]
            dic = {}
            for key, value in chunks:
                dic[key] = value
            yield dic


def convert_int_to_custom_base64(number):
    """
    int 형 자료를, 임의 base64 커스텀 문자로 변환.
    소트키 정렬 문자로 사용
    :param number:
    :return:
    """
    letters = ''
    rx = 64
    while True:
        md = number % rx
        number = number // rx
        letters = BASE64_LETTERS[md] + letters
        if number == 0:
            break

    return letters


def convert_custom_base64_to_int(custom_base64):
    """
    진법변환 커스텀임
    :param custom_base64:
    :return:
    """
    number = 0
    rx = 64
    for r, c in enumerate(custom_base64[::-1]):
        idx = BASE64_LETTERS.index(c)
        number += idx * pow(rx, r)
    return number


if __name__ == '__main__':
    n = convert_custom_base64_to_int('ciCW6QfdKjPwA')
    print(n)
