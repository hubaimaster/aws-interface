
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from botocore.errorfactory import ClientError
from numbers import Number
from dashboard.models import Log

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
        try:
            result = func(*args, **kwargs)
        except ClientError as ex:
            title = 'Unknown Error'
            desc = _('An unknown error has occurred.')
            link = None
            link_desc = None

            request = args[1]
            context = Util.get_context(request)
            url = str(request.build_absolute_uri())

            event = 'URL "{}"'.format(url)
            event = '{}\n{}'.format(event, traceback.format_exc())
            Util.log('error', request.user, event)

            error_type = None
            code = ex.response.get('Error', {}).get('Code', None)
            if code == 'UnrecognizedClientException':
                title = _('Please check the registered IAM AccessKey')
                desc = _('Invalid AccessKey entered')
                error_type = 'invalid_access_key'
            elif code == 'AccessDeniedException':
                title = _('The registered IAM AccessKey is insufficient')
                desc = _('Add the AdminUser privilege by referring to the guide link below')
                link = _('https://aws-interface.com/docs/start_awsi.pdf')
                link_desc = _('Adding AWS IAM AccessKey permissions')
                error_type = 'invalid_access_key'
            elif code == 'ResourceNotFoundException':
                title = _("Wait a minute, I'm creating a backend service.")
                desc = _('It may take up to 3 minutes')
                error_type = 'allocating'
            elif code == 'ValidationException':
                title = _('The system may be creating a backend service')
                desc = _('It may take up to 3 minutes')
                error_type = 'allocating'
            else:
                # raise ex
                pass

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
