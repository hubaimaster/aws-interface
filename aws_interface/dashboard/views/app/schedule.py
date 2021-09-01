from core.adapter.django import DjangoAdapter
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from dashboard.views.utils import Util, page_manage
from django.template import loader


class Schedule(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api, adapter.open_api_logic() as logic_api:
            context['user_groups'] = auth_api.get_user_groups()['groups']
            context['functions'] = logic_api.get_functions()['items']

        return render(request, 'dashboard/app/schedule.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_schedule() as schedule_api:
            if cmd == 'get_schedules':
                start_key = request.POST.get('start_key', None)
                return JsonResponse(schedule_api.get_schedules(start_key))
            elif cmd == 'create_schedule':
                schedule_name = request.POST.get('schedule_name')
                schedule_expression = request.POST.get('schedule_expression')
                function_name = request.POST.get('function_name')
                payload = request.POST.get('payload')
                print(schedule_name, schedule_expression, function_name, payload)
                try:
                    session_id = adapter.generate_session_id(['admin'])
                    result = schedule_api.create_schedule(schedule_name, schedule_expression, function_name, payload, session_id)
                    return JsonResponse(result)
                except Exception as e:
                    return JsonResponse({
                        'message': str(e),
                        'success': False
                    })
            elif cmd == 'delete_schedule':
                schedule_name = request.POST.get('schedule_name')
                return JsonResponse(schedule_api.delete_schedule(schedule_name))
            elif cmd == 'get_schedule':
                schedule_name = request.POST.get('schedule_name')
                return JsonResponse(schedule_api.get_schedule(schedule_name))
            elif cmd == 'get_schedule_rows':
                start_key = request.POST.get('start_key', None)
                result = schedule_api.get_schedules(start_key, reverse=True)
                template = loader.get_template('dashboard/app/component/schedule_table_row.html')
                items = result.get('items', [])
                print(items)
                end_key = result.get('end_key', None)
                context = {
                    'items': items,
                }
                result = {
                    'rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)