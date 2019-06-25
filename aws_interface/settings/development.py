from .base import *


DEBUG = True

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}

# AWS Access
AWS_ACCESS_KEY_ID = secrets_base['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = secrets_base['AWS_SECRET_KEY']

# Uncomment when test s3 upload code
# # S3 Storage
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_BUCKET_NAME = 'aws-interface-django-storage-dev'
# AWS_DEFAULT_ACL = None
# AWS_S3_REGION_NAME = "ap-northeast-2"
# AWS_S3_SIGNATURE_VERSION = "s3v4"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')
MEDIA_URL = '/media/'
