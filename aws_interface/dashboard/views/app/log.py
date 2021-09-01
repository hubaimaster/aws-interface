
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.adapter.django import DjangoAdapter
from django.http import JsonResponse
from django.template import loader
from dashboard.views.utils import Util, page_manage
import json


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

    def post(self, request, app_id):
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_log() as log:
            if cmd == 'get_logs':
                start_key = request.POST.get('start_key', None)
                event_source = request.POST.get('event_source', None)
                event_name = request.POST.get('event_name', None)
                event_param = request.POST.get('event_param', None)
                user_id = request.POST.get('user_id', None)

                log_result = log.get_logs(event_source, event_name, event_param, user_id, start_key, limit=50)
                return JsonResponse(log_result)
            elif cmd == 'get_log_rows':
                start_key = request.POST.get('start_key', None)
                event_source = request.POST.get('event_source', None)
                event_name = request.POST.get('event_name', None)
                event_param = request.POST.get('event_param', None)
                user_id = request.POST.get('user_id', None)

                result = log.get_logs(event_source, event_name, event_param, user_id, start_key, reverse=True, limit=50)
                template = loader.get_template('dashboard/app/component/log_table_row.html')
                items = result.get('items', [])

                def get_event_param(_event_param):
                    try:
                        if isinstance(_event_param, dict):
                            return json.dumps(json.loads(_event_param), sort_keys=True, indent=4)
                    except Exception as _:
                        pass
                    return str(_event_param)

                items = [{
                    'owner': item.get('owner', None),
                    'creation_date': item.get('creation_date'),
                    'event_source': item.get('event_source', None),
                    'event_name': item.get('event_name', None),
                    'event_param': get_event_param(item.get('event_param')),
                } for item in items if item.get('event_param')]
                end_key = result.get('end_key', None)
                context = {
                    'items': items,
                }
                result = {
                    'rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)
