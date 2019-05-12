
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.adapter.django import DjangoAdapter

from dashboard.views.utils import Util, page_manage


class Log(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        adapter = DjangoAdapter(app_id, request)

        event_source = request.GET.get('event_source', None)
        event_name = request.GET.get('event_name', None)
        event_param = request.GET.get('event_param', None)
        user_id = request.GET.get('user_id', None)

        context['app_id'] = app_id
        if event_source:
            context['event_source'] = event_source
        if event_name:
            context['event_name'] = event_name
        if event_param:
            context['event_param'] = event_param
        if user_id:
            context['user_id'] = user_id

        with adapter.open_api_log() as log:
            log_result = log.get_logs(event_source, event_name, event_param, user_id)
            context['logs'], context['end_key'] = log_result['items'], log_result['end_key']
            return render(request, 'dashboard/app/log.html', context=context)
