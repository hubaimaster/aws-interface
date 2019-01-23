import warnings

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.models import *

from core.api import *


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
    def is_login(cls, request):
        warnings.warn('is_login is deprecated. ask Namgyu for info')
        return request.session.get('is_login', False)

    @classmethod
    def set_login(cls, request, is_login, bundle={}):
        request.session['is_login'] = is_login
        request.session['bundle'] = bundle

    @classmethod
    def get_bundle(cls, request):
        return request.session.get('bundle', {})

    @classmethod
    def get_user_id(cls, request):
        # deprecated
        warnings.warn('get_user_id is deprecated. ask Namgyu for info')
        return request.user.id

    @classmethod
    def get_context(cls, request):
        context = dict()
        cls.__pop_alert(request, context)
        return context

    @classmethod
    def get_api(cls, api_class, recipe_type, request, app_id):
        recipe = Recipe.objects.filter(app_id=app_id, recipe_type=recipe_type).first()
        if recipe:
            recipe_json_string = recipe.json_string
        else:
            recipe_json_string = None
        api = api_class(Util.get_bundle(request), app_id, recipe_json_string)
        return api

    @classmethod
    def save_recipe(cls, recipe_controller, app_id):
        recipe_obj = Recipe.objects.filter(app_id=app_id, recipe_type=recipe_controller.get_recipe_type()).first()
        if recipe_obj is None:
            recipe_obj = Recipe()
        recipe_obj.app_id = app_id
        recipe_obj.json_string = recipe_controller.to_json()
        recipe_obj.recipe_type = recipe_controller.get_recipe_type()
        recipe_obj.save()

    @classmethod
    def set_cache(cls, request, key, value):
        request.session[key] = value

    @classmethod
    def get_cache(cls, request, key):
        return request.session.get(key, None)


class Index(LoginRequiredMixin, View):
    redirect_field_name = 'next'

    def get(self, request):
        return redirect('apps')


class Account(View):
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/account.html', context=context)


class Register(View):
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/register.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        aws_access_key = request.POST['access_key']
        aws_secret_key = request.POST['secret_key']

        normalized_email = get_user_model().objects.normalize_email(email)
        users = get_user_model().objects.all().filter(email=normalized_email)
        if len(users) > 0:
            if len(users) > 1:
                warnings.warn('there are {} users with email {}'.format(len(users), email))

            Util.add_alert(request, '이미 계정이 존재합니다.')
            return redirect('register')
        elif len(password) < 7:
            Util.add_alert(request, '비밀번호는 7자 이상입니다.')
            return redirect('register')
        else:
            get_user_model().objects.create_user(
                email, password,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
            )
            Util.add_alert(request, '회원가입에 성공하였습니다.')
            return redirect('index')


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = Util.get_context(request)
            return render(request, 'dashboard/login.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)

        if user is None:
            Util.add_alert(request, '로그인 정보가 틀렸습니다')
            return redirect('login')
        else:
            bundle = dict()
            bundle['access_key'] = user.get_aws_access_key(password)
            bundle['secret_key'] = user.get_aws_secret_key(password)
            Util.set_login(request, True, bundle=bundle)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)


class Logout(View):
    def get(self, request):
        request.session['access_key'] = None
        request.session['secret_key'] = None
        Util.set_login(request, False)
        logout(request)
        return redirect('index')


class Apps(LoginRequiredMixin, View):
    def get(self, request):
        context = Util.get_context(request)
        try:
            apps = App.objects.filter(user_id=request.user.id)
            apps = [{'id': app.id, 'creation_date': app.creation_date, 'name': app.name} for app in apps]
            context['apps'] = apps
        except ObjectDoesNotExist:
            context['apps'] = []
        return render(request, 'dashboard/apps.html', context=context)

    def post(self, request): # create app
        name = request.POST['name']
        user_id = Util.get_user_id(request)
        app = App.objects.filter(name=name)
        if app:
            Util.add_alert(request, '같은 이름의 어플리케이션이 존재합니다')
            return redirect('apps')
        app = App()
        app.name = name
        app.user_id = user_id
        app.save()
        Util.add_alert(request, '새로운 어플리케이션이 생성되었습니다')
        return redirect('apps')


class Overview(View):
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        return render(request, 'dashboard/app/overview.html', context=context)


class Bill(View):
    def get(self, request, app_id):
        cache_key = 'bill-context-' + app_id
        context = Util.get_cache(request, cache_key)
        if context:
            return render(request, 'dashboard/app/bill.html', context=context)
        context = Util.get_context(request)
        context['app_id'] = app_id
        api = Util.get_api(BillAPI, 'bill', request, app_id)
        context['cost'] = api.get_current_cost()
        context['usages'] = api.get_current_usage_costs()
        Util.set_cache(request, cache_key, context)
        return render(request, 'dashboard/app/bill.html', context=context)


class Auth(View):
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        api = Util.get_api(AuthAPI, 'auth', request, app_id)
        context['user_groups'] = api.get_user_groups()
        return render(request, 'dashboard/app/auth.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        api = Util.get_api(AuthAPI, 'auth', request, app_id)
        cmd = request.POST['cmd']
        if cmd == 'delete':
            name = request.POST['group_name']
            succeed = api.delete_user_group(name)
            if not succeed:
                Util.add_alert(request, '시스템 그룹은 삭제할 수 없습니다.')
        elif cmd == 'put':
            name = request.POST['group_name']
            description = request.POST['group_description']
            api.put_user_group(name, description)

        Util.save_recipe(api.get_recipe_controller(), app_id)
        return redirect(request.path_info)  # Redirect back


class Database(View):
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        return render(request, 'dashboard/app/database.html', context=context)


class Storage(View):
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        return render(request, 'dashboard/app/storage.html', context=context)


class Logic(View):
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        return render(request, 'dashboard/app/logic.html', context=context)
