import time

from resource.config import MAX_N_GRAM, BASE64_LETTERS, SK_FLOAT_DEC_FIT, MAX_REP_NUMBER_B64, HALF_REP_NUMBER_B64
import base64
import zlib


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


def str_to_base64_str(plain):
    """
    일반 문자열을 base64 형태로 변환
    :param plain:
    :return:
    """
    plain_b = plain.encode('utf-8')
    b64_b = base64.urlsafe_b64encode(plain_b)
    return b64_b.decode('utf-8')


def base64_str_to_str(b64_string):
    """
    str_to_base64_str 의 역함수
    :param b64_string:
    :return:
    """
    b64_b = b64_string.encode('utf-8')
    str_b = base64.urlsafe_b64decode(b64_b)
    return str_b.decode('utf-8')


def unsigned_number(number):
    """
    base64 로 진법변환을 위해, -범위를 밀어냅니다.
    총 표현 가능한 숫자 범위는
    -8.834235323891921e+55 ~
    +8.834235323891921e+55
    :param number:
    :return:
    """
    number *= pow(10, SK_FLOAT_DEC_FIT)
    number = int(number)
    # base64 40자리로 표현할 수 있는 최대 값 나누기 2 한 수를 더합니다.
    number += HALF_REP_NUMBER_B64
    if 0 <= number < MAX_REP_NUMBER_B64:
        return int(number)
    raise Exception('number must have range of -8.834235323891921e+55 ~ +8.834235323891921e+55')


def merge_pk_sk(pk, sk):
    """
    pk 와 sk 를 병합하여 반환, 구분자열은 & 이며 이스케이프 처리 필수
    :param pk:
    :param sk:
    :return:
    """
    return pk.replace('&', '-&') + '&' + sk.replace('&', '-&')


def split_pk_sk(merged_id):
    keys = []
    p_c = None
    buffer = ''
    for c in merged_id:
        if c == '&' and p_c != '-':
            keys.append(buffer.replace('-&', '&'))
            buffer = ''
        else:
            buffer += c
        p_c = c

    # 마지막 남은 버퍼
    if buffer:
        keys.append(buffer.replace('-&', '&'))
    # pk, sk
    return keys[0], keys[1]


if __name__ == '__main__':
    s = time.time()
    print(time.time() - s)