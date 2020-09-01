
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


def get_sdk_config(adapter):
    sdk_config = {
        'rest_api_url': adapter.get_rest_api_url(),
        'session_id': adapter.generate_session_id(['admin'])
    }
    print('sdk_config', sdk_config)
    return sdk_config


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
            webhooks = logic_api.get_webhooks()['items']
            for webhook in webhooks:
                webhook['url'] = logic_api.get_webhook_url(webhook['name'])['url']
            context['webhooks'] = webhooks
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
                sdk_config = get_sdk_config(adapter)

                zip_file.seek(0)
                zip_file_bin = zip_file.read()
                zip_file_bin = base64.b64encode(zip_file_bin)
                zip_file_bin = zip_file_bin.decode('utf-8')
                if not description:
                    description = None
                logic_api.create_function(function_name, description, runtime, handler, sdk_config, zip_file_bin, True)
            elif cmd == 'create_function_test':
                test_name = request.POST.get('test_name')
                function_name = request.POST.get('function_name')
                test_input = request.POST.get('test_input')
                logic_api.create_function_test(test_name, function_name, test_input)
            elif cmd == 'run_function':
                with adapter.open_sdk() as sdk_client:
                    # TODO SDK Sign-up Login and authentication takes a lot of time.
                    #  We are planning to store the SDK ID Password in the session.
                    function_name = request.POST.get('function_name')
                    payload = request.POST.get('payload')
                    payload = json.loads(payload)
                    start = time.time()
                    data = sdk_client.logic_run_function(function_name, payload)
                    end = time.time()
                    data['duration'] = end - start
                    print('data:', data)
                    return JsonResponse(data)
            elif cmd == 'delete_function_test':
                test_name = request.POST.get('test_name')
                logic_api.delete_function_test(test_name)
            elif cmd == 'delete_function':
                function_name = request.POST.get('function_name')
                function_version = request.POST.get('function_version', None)
                logic_api.delete_function(function_name, function_version)
            elif cmd == 'create_webhook':
                name = request.POST.get('name')
                description = request.POST.get('description')
                function_name = request.POST.get('function_name')
                logic_api.create_webhook(name, description, function_name)
            elif cmd == 'delete_webhook':
                name = request.POST.get('name')
                logic_api.delete_webhook(name)

        return redirect(request.path_info)  # Redirect back


class LogicEdit(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id, function_name, function_version=None):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            function = logic_api.get_function(function_name, function_version)
            function = function['item']
            file_paths = logic_api.get_function_file_paths(function_name, function_version).get('file_paths', [])
            handler_prefix = '/'.join(function['handler'].split('.')[:-1])
            current_path = None
            for file_path in file_paths:
                if file_path.startswith(handler_prefix):
                    current_path = file_path

            context['function'] = function
            context['file_paths'] = file_paths
            context['current_path'] = current_path
            context['current_file'] = logic_api.get_function_file(function_name, current_path, function_version).get('item')
        return render(request, 'dashboard/app/logic_edit.html', context=context)

    def post(self, request, app_id, function_name, function_version=None):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            if cmd == 'get_function_file':
                function_name = request.POST.get('function_name')
                function_version = request.POST.get('function_version', None)
                file_path = request.POST.get('file_path')
                result = logic_api.get_function_file(function_name, file_path, function_version)
                return JsonResponse(result)
            elif cmd == 'put_function_file':
                function_name = request.POST.get('function_name')
                function_version = request.POST.get('function_version', None)
                file_path = request.POST.get('file_path')
                file_content = request.POST.get('file_content')
                file_type = request.POST.get('file_type', 'text')
                result = logic_api.put_function_file(function_name, file_path, file_content, file_type, function_version)
                allocate_resource_in_background(adapter)
                return JsonResponse(result)
            elif cmd == 'update_function':
                function_name = request.POST.get('function_name', None)
                function_version = request.POST.get('function_version', None)
                description = request.POST.get('description', None)
                handler = request.POST.get('handler', None)
                runtime = request.POST.get('runtime', None)
                sdk_config = get_sdk_config(adapter)
                result = logic_api.update_function(function_name=function_name, description=description,
                                                   handler=handler, runtime=runtime, sdk_config=sdk_config,
                                                   function_version=function_version)
                return JsonResponse(result)
            elif cmd == 'get_function_file_paths':
                function_name = request.POST.get('function_name')
                function_version = request.POST.get('function_version', None)
                item = logic_api.get_function_file_paths(function_name, function_version)
                return JsonResponse(item)
