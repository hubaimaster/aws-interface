from .base import *

DEBUG = True

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}

# S3 Storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AWS Access
AWS_ACCESS_KEY_ID = secrets_base['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = secrets_base['AWS_SECRET_KEY']
AWS_STORAGE_BUCKET_NAME = 'aws-interface-django-storage-dev'
AWS_DEFAULT_ACL = None
