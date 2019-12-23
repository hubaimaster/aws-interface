
from core.adapter.django import DjangoAdapter
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from dashboard.views.utils import Util, page_manage
from dashboard.views.app.overview import allocate_resource_in_background

import json
import base64
import time


class Schedule(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api, adapter.open_api_logic() as logic_api:
            context['user_groups'] = auth_api.get_user_groups()['groups']
            context['functions'] = logic_api.get_functions()['items']
            context['function_tests'] = logic_api.get_function_tests()['items']
            webhooks = logic_api.get_webhooks()['items']
            for webhook in webhooks:
                webhook['url'] = logic_api.get_webhook_url(webhook['name'])['url']
            context['webhooks'] = webhooks
        return render(request, 'dashboard/app/schedule.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as api:
            if cmd == 'create_email_provider':
                api.create_email_provider()

        return redirect(request.path_info)  # Redirect back
