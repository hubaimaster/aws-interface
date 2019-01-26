#-*- coding: utf-8 -*-

import pyaes
import base64
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


class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, message):
        aes = pyaes.AESModeOfOperationCTR(self.key)
        enc = message.encode()
        enc = base64.b64encode(enc)
        enc = aes.encrypt(enc)
        enc = base64.b64encode(enc)
        enc = enc.decode()
        return enc

    def decrypt(self, enc):
        aes = pyaes.AESModeOfOperationCTR(self.key)
        dec = enc.encode()
        dec = base64.b64decode(dec)
        dec = aes.decrypt(dec)
        dec = base64.b64decode(dec)
        dec = dec.decode()
        return dec


if __name__ == '__main__':
    aes = AESCipher('key')
    message = 'message'
    enc = aes.encrypt(message)
    print('enc:', enc)
    dec = aes.decrypt(enc)
    print('dec:', dec)
    salt = Salt.get_salt(32)
    print('salt:', salt)