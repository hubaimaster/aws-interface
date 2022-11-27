#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback

from core.adapter.django import DjangoAdapter
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from dashboard.views.utils import Util, page_manage
from zipfile import ZipFile

import json
import base64
import time
import tempfile
import subprocess
import os


def get_sdk_config(adapter, use_localhost=False):
    sdk_config = {
        'rest_api_url': adapter.get_rest_api_url(),
        'session_id': adapter.generate_session_id(['admin'])
    }
    if use_localhost:
        sdk_config['external_api_url'] = sdk_config['rest_api_url']
        sdk_config['rest_api_url'] = 'http://localhost:20131'
    # print('sdk_config', sdk_config)
    return sdk_config


def get_requirements_text_from_zipfile(zipfile_bin):
    target_file = tempfile.mktemp()
    with open(target_file, 'wb+') as fp:
        fp.write(zipfile_bin)
    extracted_path = tempfile.mkdtemp()
    with ZipFile(target_file) as zf:
        zf.extractall(extracted_path)
    requirement_file_path = os.path.join(extracted_path, 'requirements.txt')
    try:
        with open(requirement_file_path, 'r') as fp:
            return fp.read()
    except Exception as ex:
        print(ex)
        return None


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
                use_logging = request.POST['use_logging'] == 'true'
                use_traceback = request.POST['use_traceback'] == 'true'
                use_standalone = request.POST['use_standalone'] == 'true'
                sdk_config = get_sdk_config(adapter, use_localhost=False)

                zip_file.seek(0)
                zip_file_bin = zip_file.read()
                zip_file_bytes = zip_file_bin
                zip_file_bin = base64.b64encode(zip_file_bin)
                zip_file_bin = zip_file_bin.decode('utf-8')
                if not description:
                    description = None

                try:
                    requirements_text = get_requirements_text_from_zipfile(zip_file_bytes)
                except Exception as ex:
                    requirements_text = None
                    print(ex)
                    print(traceback.format_exc())

                requirements_zip_file_id = None
                response_stdout = None
                if requirements_text:
                    print('requirements_text:', requirements_text)
                    with adapter.open_sdk() as sdk_client:
                        response = sdk_client.logic_create_packages_zip(requirements_text)
                        print('logic_create_packages_zip:', response)
                        requirements_zip_file_id = response.get('zip_file_id', None)
                        response_stdout = response.get('response_stdout', None)
                        if not requirements_zip_file_id:
                            raise RuntimeError('Requirements.txt error! retry or check this.')
                # response = logic_api.create_packages_zip(requirements_text)
                # print('logic_create_packages_zip:', response)
                # requirements_zip_file_id = response.get('zip_file_id', None)

                response_function_creation = logic_api.create_function(function_name, description, runtime, handler, sdk_config, zip_file_bin, True,
                                          use_logging, use_traceback, requirements_zip_file_id, use_standalone)
                return JsonResponse({
                    'package_install_response_stdout': response_stdout,
                    'response_function_creation': response_function_creation
                })
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
                    # print('data:', data)
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
        s = time.time()
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_logic() as logic_api:
            print('s:', time.time() - s)
            function = logic_api.get_function(function_name, function_version)
            print('s:', time.time() - s)
            function = function['item']
            file_paths = logic_api.get_function_file_paths(function_name, function_version).get('file_paths', [])
            handler_prefix = '/'.join(function['handler'].split('.')[:-1])
            print('s:', time.time() - s)
            current_path = None
            for file_path in file_paths:
                if file_path.startswith(handler_prefix):
                    current_path = file_path

            context['function'] = function
            context['file_paths'] = file_paths
            context['current_path'] = current_path
            context['current_file'] = logic_api.get_function_file(function_name, current_path, function_version).get('item')
            print('s:', time.time() - s)
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

                return JsonResponse(result)
            elif cmd == 'update_function':
                function_name = request.POST.get('function_name', None)
                function_version = request.POST.get('function_version', None)
                description = request.POST.get('description', None)
                handler = request.POST.get('handler', None)
                runtime = request.POST.get('runtime', None)
                use_logging = request.POST.get('use_logging', None) == 'true'
                use_traceback = request.POST.get('use_traceback', None) == 'true'
                print('use_logging:', use_logging, type(use_logging))
                print('use_traceback:', use_traceback, type(use_traceback))
                sdk_config = get_sdk_config(adapter)
                result = logic_api.update_function(function_name=function_name, description=description,
                                                   handler=handler, runtime=runtime, sdk_config=sdk_config,
                                                   function_version=function_version, use_logging=use_logging,
                                                   use_traceback=use_traceback)
                return JsonResponse(result)
            elif cmd == 'get_function_file_paths':
                function_name = request.POST.get('function_name')
                function_version = request.POST.get('function_version', None)
                item = logic_api.get_function_file_paths(function_name, function_version)
                return JsonResponse(item)
