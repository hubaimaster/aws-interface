from .base import *
import pymysql

DEBUG = False
ALLOWED_HOSTS = ['console.aws-interface.com']

DB_ENGINE = secrets_base['DB_ENGINE']
DB_NAME = secrets_base['DB_NAME']
DB_USER = secrets_base['DB_USER']
DB_PASSWORD = secrets_base['DB_PASSWORD']
DB_HOST = secrets_base['DB_HOST']
DB_PORT = secrets_base['DB_PORT']

pymysql.install_as_MySQLdb()

DATABASES['default'] = {
    'ENGINE': DB_ENGINE,
    'NAME': DB_NAME,
    'USER': DB_USER,
    'PASSWORD': DB_PASSWORD,
    'HOST': DB_HOST,
    'PORT': DB_PORT,
}