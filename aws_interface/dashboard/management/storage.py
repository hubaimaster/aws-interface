from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    # 만약 settings에서 MEDIAFILES_LOCATION을 불러오려면 다음과 같이 설정 가능
    # locaion = settings.MEDIAFILES_LOCATION
    # bucket에 미디어 파일을 넣는 directory name
    location = "mediafiles"
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super(MediaStorage, self).__init__(*args, **kwargs)


class StaticStorage(S3Boto3Storage):
    # bucket에 static 파일을 넣는 directory name
    location = "staticfiles"
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super(StaticStorage, self).__init__(*args, **kwargs)
