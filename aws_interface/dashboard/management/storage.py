from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = "mediafiles"
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super(MediaStorage, self).__init__(*args, **kwargs)


class StaticStorage(S3Boto3Storage):
    location = "staticfiles"
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super(StaticStorage, self).__init__(*args, **kwargs)
