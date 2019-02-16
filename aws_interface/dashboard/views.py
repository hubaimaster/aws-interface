import warnings

from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from dashboard.models import *
from core.api import *

from botocore.errorfactory import ClientError
from numbers import Number
from decimal import Decimal

import json
import base64


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
                title = '잠시만 기다려주세요 AWS Interface 가 백엔드 서비스를 생성중입니다'
                desc = '경우에 따라 최대 10분 정도 소요될 수 있습니다'

            context['error'] = ex
            context['title'] = title
            context['desc'] = desc
            context['link'] = link
            context['link_desc'] = link_desc
            return render(request, 'dashboard/error.html', context=context)
        return result
    return wrap


class Index(LoginRequiredMixin, View):
    redirect_field_name = 'next'

    @page_manage
    def get(self, request):
        return redirect('apps')


class AccessKey(View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/accesskey.html', context=context)

    @page_manage
    def post(self, request):
        password = request.POST['password']
        access_key = request.POST['access_key']
        secret_key = request.POST['secret_key']
        # Check AccessKey.. TODO
        request.user.set_aws_credentials(password, access_key, secret_key)
        request.user.save()

        bundle = dict()
        bundle['access_key'] = request.user.get_aws_access_key(password)
        bundle['secret_key'] = request.user.get_aws_secret_key(password)
        Util.set_login(request, True, bundle=bundle)
        Util.add_alert(request, 'AccessKey 를 변경하였습니다.')
        return redirect('apps')


class Register(View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/register.html', context=context)

    @page_manage
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
    @page_manage
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = Util.get_context(request)
            return render(request, 'dashboard/login.html', context=context)

    @page_manage
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
    @page_manage
    def get(self, request):
        request.session['access_key'] = None
        request.session['secret_key'] = None
        Util.set_login(request, False)
        logout(request)
        return redirect('index')


class Apps(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        try:
            apps = App.objects.filter(user_id=request.user.id)
            apps = [{'id': app.id, 'creation_date': app.creation_date, 'name': app.name} for app in apps]
            context['apps'] = apps
        except ObjectDoesNotExist:
            context['apps'] = []
        return render(request, 'dashboard/apps.html', context=context)

    @page_manage
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
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id)
        context['app_id'] = app_id
        context['app_name'] = app.name
        return render(request, 'dashboard/app/overview.html', context=context)


class Guide(View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id)
        context['app_id'] = app_id
        context['app_name'] = app.name
        return render(request, 'dashboard/app/guide.html', context=context)


class Bill(View):
    @page_manage
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
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        api = Util.get_api(AuthAPI, 'auth', request, app_id)
        cmd = request.GET.get('cmd', None)
        if cmd == 'download_sdk':
            api.apply()
            sdk_bin = api.get_rest_api_sdk()
            response = HttpResponse(sdk_bin, content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename('auth_sdk.zip')
            return response
        else:
            context['user_groups'] = api.get_user_groups()
            context['user_count'] = api.get_user_count()
            context['session_count'] = api.get_session_count()
            context['users'] = api.get_users()
            context['email_login'] = api.get_email_login()
            context['guest_login'] = api.get_guest_login()
            context['rest_api_url'] = api.get_rest_api_url()
            return render(request, 'dashboard/app/auth.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        api = Util.get_api(AuthAPI, 'auth', request, app_id)
        cmd = request.POST['cmd']

        # Recipe
        if cmd == 'delete_group':
            name = request.POST['group_name']
            succeed = api.delete_user_group(name)
            if not succeed:
                Util.add_alert(request, '시스템 그룹은 삭제할 수 없습니다.')
            api.apply()
        elif cmd == 'put_group':
            name = request.POST['group_name']
            description = request.POST['group_description']
            api.put_user_group(name, description)
            api.apply()
        elif cmd == 'set_email_login':
            default_group = request.POST['email_default_group']
            enabled = request.POST['email_enabled']
            if enabled == 'true':
                enabled = True
            else:
                enabled = False
            api.set_email_login(enabled, default_group)
            api.apply()
        elif cmd == 'set_guest_login':
            default_group = request.POST['guest_default_group']
            enabled = request.POST['guest_enabled']
            if enabled == 'true':
                enabled = True
            else:
                enabled = False
            api.set_guest_login(enabled, default_group)
            api.apply()

        # Service
        elif cmd == 'put_user':
            email = request.POST['user_email']
            password = request.POST['user_password']
            api.create_user(email, password, {})
        elif cmd == 'delete_user':
            user_id = request.POST['user_id']
            api.delete_user(user_id)

        Util.save_recipe(api.get_recipe_controller(), app_id)
        return redirect(request.path_info)  # Redirect back


class Database(View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        auth = Util.get_api(AuthAPI, 'auth', request, app_id)
        database = Util.get_api(DatabaseAPI, 'database', request, app_id)
        context['app_id'] = app_id
        cmd = request.GET.get('cmd', None)

        if cmd == 'download_sdk':
            database.apply()
            Util.save_recipe(database.get_recipe_controller(), app_id)
            sdk_bin = database.get_rest_api_sdk()
            response = HttpResponse(sdk_bin, content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename('database_sdk.zip')
            return response
        else:
            partitions = database.get_partitions()
            partitions = Util.encode_dict(partitions)
            for partition in partitions:
                result = database.get_item_count(partition)
                partitions[partition]['item_count'] = result['item']['count']
            partitions = partitions.values()

            context['user_groups'] = auth.get_user_groups()
            context['partitions'] = partitions
            context['rest_api_url'] = database.get_rest_api_url()
            return render(request, 'dashboard/app/database.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        database = Util.get_api(DatabaseAPI, 'database', request, app_id)
        cmd = request.POST['cmd']

        if cmd == 'add_partition':
            partition_name = request.POST['partition_name']
            _ = database.put_partition(partition_name)
            database.apply()
        elif cmd == 'add_item':
            partition = request.POST['partition']
            read_groups = request.POST.getlist('read_groups[]')
            write_groups = request.POST.getlist('write_groups[]')
            _ = database.create_item(partition, {}, read_groups, write_groups)
        elif cmd == 'add_field':
            item_id = request.POST['item_id']
            field_name = request.POST['field_name']
            field_value = request.POST['field_value']
            field_type = request.POST['field_type']
            if field_type == 'S':
                field_value = str(field_value)
            elif field_type == 'N':
                field_value = Decimal(field_value)
            elif field_type == 'L':
                field_value = list(field_value)
            _ = database.put_item_field(item_id, field_name, field_value)
        elif cmd == 'delete_partition':
            partition_name = request.POST['partition_name']
            _ = database.delete_partition(partition_name)

        elif cmd == 'get_items':
            partition = request.POST['partition']
            result = database.get_items(partition)
            result = Util.encode_dict(result)
            return JsonResponse(result)
        elif cmd == 'get_item':
            item_id = request.POST['item_id']
            result = database.get_item(item_id)
            result = Util.encode_dict(result)
            return JsonResponse(result)
        elif cmd == 'delete_item':
            item_id = request.POST['item_id']
            result = database.delete_item(item_id)
            return JsonResponse(result)
        elif cmd == 'delete_field':
            item_id = request.POST['item_id']
            field_name = request.POST['field_name']
            result = database.put_item_field(item_id, field_name, None)
            return JsonResponse(result)
        elif cmd == 'get_item_count':
            partition = request.POST['partition']
            result = database.get_item_count(partition)
            result = Util.encode_dict(result)
            return JsonResponse(result)

        Util.save_recipe(database.get_recipe_controller(), app_id)
        return redirect(request.path_info)  # Redirect back


class Storage(View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        auth = Util.get_api(AuthAPI, 'auth', request, app_id)
        storage = Util.get_api(StorageAPI, 'storage', request, app_id)
        cmd = request.GET.get('cmd', None)
        if cmd == 'download_sdk':
            storage.apply()
            Util.save_recipe(storage.get_recipe_controller(), app_id)
            sdk_bin = storage.get_rest_api_sdk()
            response = HttpResponse(sdk_bin, content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename('storage_sdk.zip')
            return response
        elif cmd == 'download_file':
            file_path = request.GET['file_path']
            file_name = file_path.split('/').pop()
            file_bin_b64 = storage.download_file(file_path)
            file_bin = base64.b64decode(file_bin_b64)
            response = HttpResponse(file_bin, content_type='application/x-binary')
            file_name = file_name.encode('utf8').decode('ISO-8859-1')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_name)
            return response
        else:
            folder_path = request.GET.get('folder_path', '/')
            start_key = request.GET.get('start_key', None)
            context['app_id'] = app_id
            context['folder_path'] = folder_path
            context['user_groups'] = auth.get_user_groups()
            context['rest_api_url'] = storage.get_rest_api_url()
            context['folder_list'] = storage.get_folder_list(folder_path, start_key)
            return render(request, 'dashboard/app/storage.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        storage = Util.get_api(StorageAPI, 'storage', request, app_id)
        cmd = request.POST['cmd']
        if cmd == 'create_folder':
            parent_path = request.POST['parent_path']
            folder_name = request.POST['folder_name']
            read_groups = request.POST.getlist('read_groups[]')
            write_groups = request.POST.getlist('write_groups[]')
            result = storage.create_folder(parent_path, folder_name, read_groups, write_groups)
            return JsonResponse(result)
        elif cmd == 'upload_file':
            parent_path = request.POST['parent_path']
            file_bin = request.FILES['file_bin']
            file_name = request.POST['file_name']
            read_groups = json.loads(request.POST.get('read_groups'))
            write_groups = json.loads(request.POST.get('write_groups'))

            result = storage.upload_file(parent_path, file_name, file_bin, read_groups, write_groups)
            return JsonResponse(result)
        elif cmd == 'get_folder_list':
            folder_path = request.POST['folder_path']
            start_key = request.POST.get('start_key', None)
            result = storage.get_folder_list(folder_path, start_key)
            return JsonResponse(result)
        elif cmd == 'download_file':
            file_path = request.POST['file_path']
            file_bin = storage.download_file(file_path)
            response = HttpResponse(file_bin, content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename('storage_sdk.zip')
            return response
        elif cmd == 'delete_file':
            file_path = request.POST['file_path']
            result = storage.delete_file(file_path)
            return JsonResponse(result)
        elif cmd == 'delete_folder':
            folder_path = request.POST['folder_path']
            result = storage.delete_folder(folder_path)
            return JsonResponse(result)


class Logic(View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        return render(request, 'dashboard/app/logic.html', context=context)

