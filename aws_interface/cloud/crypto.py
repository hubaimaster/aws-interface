#-*- coding: utf-8 -*-
import hashlib
import os
import decimal
import base64
import tempfile
import json


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


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


class Base64:
    @classmethod
    def dict_to_base64(cls, obj):
        obj = json.dumps(obj, default=decimal_default)
        obj = obj.encode('utf-8')
        obj = base64.b64encode(obj)
        obj = obj.decode('utf-8')
        return obj

    @classmethod
    def base64_to_dict(cls, text):
        text = base64.b64decode(text)
        text = text.decode('utf-8')
        obj = json.loads(text)
        cls.use_decimal(obj)
        return obj

    @classmethod
    def use_decimal(cls, json_obj):
        for node in json_obj:
            if type(json_obj[node]) is float or type(json_obj[node]) is int:
                json_obj[node] = decimal.Decimal(json_obj[node])

    @classmethod
    def file_bin_to_base64(cls, file_bin):
        output = file_bin.read()
        output = base64.b64encode(output)
        return output

    @classmethod
    def base64_to_file_bin(cls, base64_string):
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        base64_bin = base64.b64decode(base64_string)
        fin = tempfile.NamedTemporaryFile()
        fin.write(base64_bin)
        return fin
