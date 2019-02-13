import math
import uuid as _uuid


alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZ" "abcdefghijkmnopqrstuvwxyz")
alphabet = list(sorted(set(alphabet)))
_alphabet = alphabet
_alpha_len = len(_alphabet)
_length = int(math.ceil(math.log(2 ** 128, _alpha_len)))


def _int_to_string(number, alphabet, padding=None):
    output = ""
    alpha_len = len(alphabet)
    while number:
        number, digit = divmod(number, alpha_len)
        output += alphabet[digit]
    if padding:
        remainder = max(padding - len(output), 0)
        output = output + alphabet[0] * remainder
    return output[::-1]


def _encode(uuid):
    pad_length = _length
    return _int_to_string(uuid.int, _alphabet, padding=pad_length)


def uuid():
    uuid = _uuid.uuid4()
    return _encode(uuid)
