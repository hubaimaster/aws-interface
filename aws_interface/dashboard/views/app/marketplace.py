
from core.adapter.django import DjangoAdapter

from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist

from dashboard.models import App, MarketplaceLogic, MarketplaceLogicSetup
from dashboard.views.utils import Util, page_manage
from dashboard.message import error
from dashboard.views.app.logic import get_sdk_config

import base64


CATEGORIES = {
    'example': 'Example',
    'api_bridge': 'API Bridge',
    'machine_learning': 'Machine Learning',
    'utilities': 'Utilities',
    'messaging': 'Messaging',
}


class Marketplace(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)

        my_marketplace_logics = MarketplaceLogic.objects.filter(user=request.user).order_by('creation_date').reverse()[:100]
        marketplace_logics = MarketplaceLogic.objects.order_by('creation_date').reverse()[:100]
        top_setup_marketplace_logics = MarketplaceLogic.objects.order_by('setup_count').reverse()[:2]

        context['app_id'] = app_id
        context['app_name'] = app.name
        context['marketplace_logics'] = marketplace_logics
        context['my_marketplace_logics'] = my_marketplace_logics
        context['top_setup_marketplace_logics'] = top_setup_marketplace_logics
        return render(request, 'dashboard/app/marketplace.html', context=context)


class MarketplaceCreate(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
        context['categories'] = CATEGORIES.items()
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            context['functions'] = logic_api.get_functions()['items']
        return render(request, 'dashboard/app/marketplace_create.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
        adapter = DjangoAdapter(app_id, request)
        cmd = request.POST.get('cmd', None)
        if cmd == 'upload_marketplace_logic':
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category')
            logo_image = request.FILES.get('logo_image')
            content = request.POST.get('content')
            function_name = request.POST.get('function_name')
            with adapter.open_api_logic() as logic_api:
                result = logic_api.get_function(function_name)
                if 'error' in result:
                    return JsonResponse(result)
                logic_function = result['item']
                handler = logic_function['handler']
                runtime = logic_function['runtime']
                function_zip_b64 = logic_api.get_function_zip_b64(function_name)['item']['base64']
                function_zip_b64 = function_zip_b64.encode('utf-8')
                function_zip = base64.b64decode(function_zip_b64)
                function_zip_name = '{}.zip'.format(function_name)
                function_zip_file = SimpleUploadedFile(function_zip_name, function_zip, 'application/octet-stream')

            marketplace_logic = MarketplaceLogic(user=request.user)
            marketplace_logic.title = title
            marketplace_logic.description = description
            marketplace_logic.category = category
            marketplace_logic.logo_image = logo_image
            marketplace_logic.content = content
            marketplace_logic.function_zip_file = function_zip_file
            marketplace_logic.function_name = function_name
            marketplace_logic.handler = handler
            marketplace_logic.runtime = runtime
            marketplace_logic.save()
            return JsonResponse(data={
                'marketplace_logic_id': marketplace_logic.id
            })


class MarketplaceDetail(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id, marketplace_logic_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        try:
            marketplace_logic = MarketplaceLogic.objects.get(id=marketplace_logic_id)
        except ObjectDoesNotExist as ex:
            print(ex)
            return redirect('marketplace', app_id)

        context['app_id'] = app_id
        context['app_name'] = app.name
        context['marketplace_logic'] = marketplace_logic
        return render(request, 'dashboard/app/marketplace_detail.html', context=context)

    def post(self, request, app_id, marketplace_logic_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        marketplace_logic = MarketplaceLogic.objects.get(id=marketplace_logic_id)
        cmd = request.POST.get('cmd', None)
        if cmd == 'delete_marketplace_logic':
            if marketplace_logic.user == request.user:
                marketplace_logic.delete()
                return JsonResponse({})
            else:
                return JsonResponse({
                    'error': error.PERMISSION_DENIED
                })
        elif cmd == 'setup_marketplace_logic':
            adapter = DjangoAdapter(app_id, request)
            function_name = request.POST.get('function_name', None)
            if not function_name:
                function_name = marketplace_logic.function_name
            marketplace_logic_id = self.setup_marketplace_logic(adapter, marketplace_logic, function_name)
            self.increase_setup_count(marketplace_logic, request.user)
            return marketplace_logic_id

    @classmethod
    def increase_setup_count(cls, marketplace_logic, setup_user):
        try:
            setup = MarketplaceLogicSetup.objects.get(marketplace_logic=marketplace_logic, user=setup_user)
        except MarketplaceLogicSetup.DoesNotExist:
            setup = None
        if setup is None:
            setup = MarketplaceLogicSetup(marketplace_logic=marketplace_logic, user=setup_user)
            setup.save()
            marketplace_logic.setup_count += 1
            marketplace_logic.save()

    @classmethod
    def setup_marketplace_logic(cls, adapter, marketplace_logic, function_name):
        with adapter.open_api_logic() as logic_api:
            description = marketplace_logic.description
            runtime = marketplace_logic.runtime
            handler = marketplace_logic.handler
            sdk_config = get_sdk_config(adapter)
            zipfile = marketplace_logic.function_zip_file.read()
            zipfile = base64.b64encode(zipfile)
            zipfile = zipfile.decode('utf-8')
            result = logic_api.create_function(function_name, description, runtime, handler, sdk_config, zipfile)
            return JsonResponse(result)


class MarketplaceEdit(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id, marketplace_logic_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        marketplace_logic = MarketplaceLogic.objects.get(id=marketplace_logic_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
        context['categories'] = CATEGORIES.items()
        context['marketplace_logic'] = marketplace_logic
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            context['functions'] = logic_api.get_functions()['items']
        return render(request, 'dashboard/app/marketplace_edit.html', context=context)

    def post(self, request, app_id, marketplace_logic_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
        adapter = DjangoAdapter(app_id, request)
        cmd = request.POST.get('cmd', None)
        if cmd == 'edit_marketplace_logic':
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category')
            logo_image = request.FILES.get('logo_image')
            content = request.POST.get('content')
            function_name = request.POST.get('function_name')

            change_logo_image = request.POST.get('change_logo_image', False)
            change_function = request.POST.get('change_function', False)

            if change_logo_image == 'true':
                change_logo_image = True
            elif change_logo_image == 'false':
                change_logo_image = False

            if change_function == 'true':
                change_function = True
            elif change_function == 'false':
                change_function = False

            with adapter.open_api_logic() as logic_api:
                logic_function = logic_api.get_function(function_name)['item']
                handler = logic_function['handler']
                runtime = logic_function['runtime']
                function_zip_b64 = logic_api.get_function_zip_b64(function_name)['item']['base64']
                function_zip_b64 = function_zip_b64.encode('utf-8')
                function_zip = base64.b64decode(function_zip_b64)
                function_zip_name = '{}.zip'.format(function_name)
                function_zip_file = SimpleUploadedFile(function_zip_name, function_zip, 'application/octet-stream')

            marketplace_logic = MarketplaceLogic.objects.get(id=marketplace_logic_id, user=request.user)
            marketplace_logic.title = title
            marketplace_logic.description = description
            marketplace_logic.category = category

            if change_logo_image:
                marketplace_logic.logo_image = logo_image

            if change_function:
                # Needs security verification by AWS-I team
                marketplace_logic.verified = False
                marketplace_logic.function_zip_file = function_zip_file

            marketplace_logic.function_name = function_name
            marketplace_logic.handler = handler
            marketplace_logic.runtime = runtime
            marketplace_logic.content = content
            marketplace_logic.save()
            return JsonResponse(data={
                'marketplace_logic_id': marketplace_logic.id
            })
