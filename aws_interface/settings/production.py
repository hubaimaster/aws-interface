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

# AWS Access
AWS_ACCESS_KEY_ID = secrets_base['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = secrets_base['AWS_SECRET_KEY']

# S3 Storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'aws-interface-django-storage'
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = "ap-northeast-2"
AWS_S3_SIGNATURE_VERSION = "s3v4"
