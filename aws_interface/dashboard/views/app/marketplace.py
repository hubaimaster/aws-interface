
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.adapter.django import DjangoAdapter

from dashboard.models import *
from dashboard.views.utils import Util, page_manage


class Marketplace(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        app = App.objects.get(id=app_id, user=request.user)
        context['app_id'] = app_id
        context['app_name'] = app.name
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
