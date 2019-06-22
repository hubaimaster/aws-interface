
from core.adapter.django import DjangoAdapter

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import SimpleUploadedFile

from dashboard.models import App, MarketplaceLogic
from dashboard.views.utils import Util, page_manage

import base64


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


class MarketplaceEdit(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            context['functions'] = logic_api.get_functions()['items']
        return render(request, 'dashboard/app/marketplace_edit.html', context=context)

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
                logic_function = logic_api.get_function(function_name)['item']
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
        marketplace_logic = MarketplaceLogic.objects.get(id=marketplace_logic_id)

        context['app_id'] = app_id
        context['app_name'] = app.name
        context['marketplace_logic'] = marketplace_logic
        return render(request, 'dashboard/app/marketplace_detail.html', context=context)
