
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from dashboard.views.utils import Util, page_manage
from core.adapter.django import DjangoAdapter
import json
import base64


class Logic(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api, adapter.open_api_logic() as logic_api:
            context['user_groups'] = auth_api.get_user_groups()['groups']
            context['functions'] = logic_api.get_functions()['items']
            context['function_tests'] = logic_api.get_function_tests()['items']
        return render(request, 'dashboard/app/logic.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            if cmd == 'create_function':
                zip_file = request.FILES['zip_file']
                function_name = request.POST['function_name']
                description = request.POST['description']
                runtime = request.POST['runtime']
                handler = request.POST['handler']
                zip_file.seek(0)
                zip_file_bin = zip_file.read()
                zip_file_bin = base64.b64encode(zip_file_bin)
                zip_file_bin = zip_file_bin.decode('utf-8')
                logic_api.create_function(function_name, description, runtime, handler, zip_file_bin, True)
            elif cmd == 'create_function_test':
                test_name = request.POST.get('test_name')
                function_name = request.POST.get('function_name')
                test_input = request.POST.get('test_input')
                logic_api.create_function_test(test_name, function_name, test_input)
            elif cmd == 'run_function':
                # TODO It could be serious problem -> User can invoke dangerous code via run_function
                #  Using SDK to solve this [ Run on cloud server-less service ]
                sdk_client = adapter.get_sdk()

                function_name = request.POST.get('function_name')
                payload = request.POST.get('payload')
                payload = json.loads(payload)
                sdk_client.auth_guest()
                data = sdk_client.logic_run_function(function_name, payload)
                # data = logic_api.run_function(function_name, payload)
                return JsonResponse(data)
            elif cmd == 'delete_function_test':
                test_name = request.POST.get('test_name')
                logic_api.delete_function_test(test_name)
            elif cmd == 'delete_function':
                function_name = request.POST.get('function_name')
                logic_api.delete_function(function_name)

        return redirect(request.path_info)  # Redirect back


class LogicEdit(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id, function_name):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            function = logic_api.get_function(function_name)['item']
            file_paths = logic_api.get_function_file_paths(function_name).get('file_paths', [])
            handler_prefix = '/'.join(function['handler'].split('.')[:-1])
            current_path = None
            for file_path in file_paths:
                if file_path.startswith(handler_prefix):
                    current_path = file_path

            context['function'] = function
            context['file_paths'] = file_paths
            context['current_path'] = current_path
            context['current_file'] = logic_api.get_function_file(function_name, current_path)['item']

        return render(request, 'dashboard/app/logic_edit.html', context=context)

    def post(self, request, app_id, function_name):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            if cmd == 'get_function_file':
                function_name = request.POST.get('function_name')
                file_path = request.POST.get('file_path')
                result = logic_api.get_function_file(function_name, file_path)
                return JsonResponse(result)
            if cmd == 'put_function_file':
                function_name = request.POST.get('function_name')
                file_path = request.POST.get('file_path')
                file_content = request.POST.get('file_content')
                file_type = request.POST.get('file_type', 'text')
                result = logic_api.put_function_file(function_name, file_path, file_content, file_type)
                return JsonResponse(result)
