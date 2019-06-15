
from django.shortcuts import render, redirect
from botocore.errorfactory import ClientError
from numbers import Number
from dashboard.models import App, Log
from dashboard.management.tracking import Tracking
import traceback


class Util:
    @classmethod
    def _pop_alert(cls, request, context):
        alert = request.session.get('alert', None)
        request.session['alert'] = None
        context['alert'] = alert

    @classmethod
    def add_alert(cls, request, alert):
        request.session['alert'] = alert

    @classmethod
    def get_credentials(cls, request):
        return request.session.get('credentials', {})

    @classmethod
    def reset_credentials(cls, request, credentials={}):
        request.session['credentials'] = credentials

    @classmethod
    def get_context(cls, request):
        context = dict()
        cls._pop_alert(request, context)
        return context

    @classmethod
    def set_cache(cls, request, key, value):
        request.session[key] = value

    @classmethod
    def get_cache(cls, request, key):
        return request.session.get(key, None)

    @classmethod
    def encode_dict(cls, dict_obj):
        def cast_number(v):
            if isinstance(v, dict):
                return cls.encode_dict(v)
            if not isinstance(v, Number):
                return v
            if v % 1 == 0:
                return int(v)
            else:
                return float(v)
        return {k: cast_number(v) for k, v in dict_obj.items()}

    @classmethod
    def is_valid_access_key(cls, aws_access_key, aws_secret_key):
        if not aws_access_key:
            return False
        if not aws_secret_key:
            return False
        if len(aws_access_key) < 4:
            return False
        if len(aws_secret_key) < 4:
            return False
        return True

    @classmethod
    def log(cls, level, user, event):
        level = level.lower()
        if not user.is_authenticated:
            user = None
        log = Log(level=level, user=user, event=event)
        log.save()


def page_manage(func):
    def wrap(*args, **kwargs):
        try:  # Logging
            request = args[1]
            url = str(request.build_absolute_uri())
            Tracking(request).view_url(url)
            event = 'func:{}, args:{}, kwargs:{}'.format(func, args, kwargs)
            Util.log('info', request.user, event)
        except Exception as ex:
            print(ex)
        try:
            result = func(*args, **kwargs)
        except ClientError as ex:
            title = 'Unknown Error'
            desc = '원인을 알 수 없는 에러입니다'
            link = None
            link_desc = None

            request = args[1]
            context = Util.get_context(request)
            url = str(request.build_absolute_uri())

            event = 'URL "{}"'.format(url)
            event = '{}\n{}'.format(event, traceback.format_exc())

            Util.log('error', request.user, event)
            print(event)

            code = ex.response.get('Error', {}).get('Code', None)
            error_type = None
            if code == 'UnrecognizedClientException':
                title = '등록된 IAM AccessKey 를 확인해주세요'
                desc = '유효하지 않은 AccessKey 가 입력되어 있습니다'
                error_type = 'invalid_access_key'
            elif code == 'AccessDeniedException':
                title = '등록된 IAM AccessKey 의 권한이 부족합니다'
                desc = '아래 가이드 링크를 참고하여 AdminUser 권한을 추가합니다'
                link = 'https://aws-interface.com/docs/start_awsi.pdf'
                link_desc = 'AWS IAM AccessKey 권한 추가하기'
                error_type = 'invalid_access_key'
            elif code == 'ResourceNotFoundException':
                title = '잠시만 기다려주세요 백엔드 서비스를 생성중 입니다'
                desc = '경우에 따라 최대 3분 정도 소요될 수 있습니다'
                error_type = 'allocating'
            elif code == 'ValidationException':
                title = '백엔드 서비스를 생성중 일 수 있습니다'
                desc = '경우에 따라 최대 10분 정도 소요될 수 있습니다'
                error_type = 'allocating'

            context['error'] = ex
            context['error_type'] = error_type
            context['title'] = title
            context['desc'] = desc
            context['link'] = link
            context['link_desc'] = link_desc
            context['code'] = code
            context['app_id'] = kwargs.get('app_id', None)

            return render(request, 'dashboard/error.html', context=context)
        return result
    return wrap
