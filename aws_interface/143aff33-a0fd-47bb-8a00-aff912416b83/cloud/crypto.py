#-*- coding: utf-8 -*-
import hashlib
import os


class Salt:
    @classmethod
    def get_salt(cls, size):
        return os.urandom(size).hex()


class Hash:
    @classmethod
    def sha3_512(cls, plain):
        plain = plain.encode()
        hash = hashlib.sha3_512(plain)
        hash = str(hash.hexdigest())
        return hash


def hash_password(password, salt):
    return Hash.sha3_512(password + salt)
