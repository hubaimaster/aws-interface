
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from dashboard.models import *
from botocore.errorfactory import ClientError
from numbers import Number
from resource import get_resource_allocator
from core.recipe_controller import rc_dict


class Util:
    @classmethod
    def __pop_alert(cls, request, context):
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
        cls.__pop_alert(request, context)
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
    def create_app(cls, request):
        name = request.POST['name']
        if not name or len(name) < 3:
            Util.add_alert(request, '이름은 3글자 이상입니다')
            return redirect('apps')
        user_id = request.user.id
        app = App.objects.filter(user=request.user.id, name=name)
        if app:
            Util.add_alert(request, '같은 이름의 어플리케이션이 존재합니다')
            return redirect('apps')
        app = App()
        app.name = name
        app.user_id = user_id
        app.save()
        Util.add_alert(request, '새로운 어플리케이션이 생성되었습니다')

    @classmethod
    def init_recipes(cls, app):
        from core.recipe_controller import rc_dict
        for name, recipe_cls in rc_dict.items():
            default_json_string = recipe_cls().to_json_string()
            try:
                recipe = Recipe.objects.get(app=app, name=name)
                if not recipe.json_string:
                    recipe.json_string = default_json_string
                    recipe.save()
            except ObjectDoesNotExist as _:
                recipe = Recipe(app=app, name=name)
                recipe.json_string = default_json_string
                recipe.save()
                continue


def page_manage(func):
    def wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ClientError as ex:
            title = 'Unknown Error'
            desc = '원인을 알 수 없는 에러입니다'
            link = None
            link_desc = None

            request = args[1]
            context = Util.get_context(request)
            code = ex.response.get('Error', {}).get('Code', None)
            if code == 'UnrecognizedClientException':
                title = '등록된 IAM AccessKey 를 확인해주세요'
                desc = '유효하지 않은 AccessKey 가 입력되어 있습니다'
            elif code == 'AccessDeniedException':
                title = '등록된 IAM AccessKey 의 권한이 부족합니다'
                desc = '아래 가이드 링크를 참고하여 AdminUser 권한을 추가합니다'
                link = 'guide'
                link_desc = 'AWS IAM AccessKey 권한 추가히기'
            elif code == 'ResourceNotFoundException':
                title = '잠시만 기다려주세요 AWS Interface 가 백엔드 서비스를 생성중 입니다'
                desc = '경우에 따라 최대 10분 정도 소요될 수 있습니다'
            elif code == 'ValidationException':
                title = 'AWS Interface 가 백엔드 서비스를 생성중 일 수 있습니다'
                desc = '경우에 따라 최대 10분 정도 소요될 수 있습니다'

            context['error'] = ex
            context['title'] = title
            context['desc'] = desc
            context['link'] = link
            context['link_desc'] = link_desc
            # TODO 에러났을때 엉키는거 방지.. 어플 디폴로이 초기화 등

            return render(request, 'dashboard/error.html', context=context)
        return result
    return wrap
