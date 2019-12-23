
from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template import loader
from dashboard.views.utils import Util, page_manage
from dashboard.views.app.overview import allocate_resource_in_background
from core.adapter.django import DjangoAdapter

import json
import base64
import os


class Storage(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        adapter = DjangoAdapter(app_id, request)
        allocate_resource_in_background(adapter)
        with adapter.open_api_auth() as auth_api, adapter.open_api_storage() as storage_api:
            cmd = request.GET.get('cmd', None)
            if cmd == 'download_file':
                file_path = request.GET['file_path']
                file_name = file_path.split('/').pop()
                file_bin_b64 = storage_api.download_b64(file_path)
                file_bin = base64.b64decode(file_bin_b64)
                response = HttpResponse(file_bin, content_type='application/x-binary')
                file_name = file_name.encode('utf8').decode('ISO-8859-1')
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_name)
                return response
            elif cmd == 'download_b64':
                file_id = request.GET['file_id']
                string_file_b64 = None
                file_name = 'file'
                while file_id:
                    result = storage_api.download_b64(file_id)
                    file_id = result.get('parent_file_id', None)
                    string_b64_chuck = result.get('file_b64')

                    if string_file_b64:
                        string_file_b64 = string_b64_chuck + string_file_b64
                    else:
                        string_file_b64 = string_b64_chuck
                    file_name = result.get('file_name', file_name)

                string_b64 = string_file_b64.encode('utf-8')
                file_bin = base64.b64decode(string_b64)

                response = HttpResponse(file_bin, content_type='application/x-binary')
                file_name = file_name.encode('utf8').decode('ISO-8859-1')
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_name)
                return response
            else:
                result = storage_api.get_b64_info_items(start_key=None, reverse=True)
                context['app_id'] = app_id
                context['b64_info'] = result
                context['user_groups'] = auth_api.get_user_groups()['groups']

        return render(request, 'dashboard/app/storage.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_storage() as storage_api:
            cmd = request.POST['cmd']
            if cmd == 'upload_b64':  # 분할 업로드
                file_bin = request.FILES['file_bin']
                file_name = request.POST['file_name']
                parent_file_id = None

                def divide_chunks(text, n):
                    for i in range(0, len(text), n):
                        yield text[i:i + n]

                raw_base64 = file_bin.read()
                raw_base64 = base64.b64encode(raw_base64)
                raw_base64 = raw_base64.decode('utf-8')
                base64_chunks = divide_chunks(raw_base64, 1024 * 1024 * 4)  # 4mb
                for base64_chunk in base64_chunks:
                    result = storage_api.upload_b64(parent_file_id, file_name, base64_chunk)
                    parent_file_id = result.get('file_id')
                return JsonResponse(result)
            elif cmd == 'get_b64_info_items':  # For admins
                start_key = request.POST.get('start_key', None)
                result = storage_api.get_b64_info_items(start_key, reverse=True)
                return JsonResponse(result)
            elif cmd == 'delete_b64':
                file_id = request.POST['file_id']
                result = storage_api.delete_b64(file_id)
                return JsonResponse(result)
            elif cmd == 'get_policy_code':
                mode = request.POST.get('mode')
                result = storage_api.get_policy_code(mode)
                return JsonResponse(result)
            elif cmd == 'put_policy':
                mode = request.POST.get('mode')
                code = request.POST.get('code')
                result = storage_api.put_policy(mode, code)
                return JsonResponse(result)
            elif cmd == 'get_file_rows':
                start_key = request.POST.get('start_key', None)
                result = storage_api.get_b64_info_items(start_key, reverse=True)
                template = loader.get_template('dashboard/app/component/storage_file_table_row.html')
                files = result.get('items', [])
                end_key = result.get('end_key', None)
                context = {
                    'app_id': app_id,
                    'files': files,
                }
                result = {
                    'file_rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)