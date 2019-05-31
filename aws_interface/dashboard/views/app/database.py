
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from core.adapter.django import DjangoAdapter
from dashboard.views.utils import Util, page_manage
from decimal import Decimal
import json


class Database(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api, adapter.open_api_database() as database_api:
            partitions = database_api.get_partitions().get('items', [])
            partition_dict = {}
            for partition in partitions:
                name = partition['name']
                result = database_api.get_item_count(name)
                partition_dict[name] = {
                    'name': name,
                    'item_count': result['item']['count']
                }
            partitions = partition_dict.values()

            context['user_groups'] = auth_api.get_user_groups()['groups']
            context['partitions'] = partitions

        return render(request, 'dashboard/app/database.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_database() as database_api:
            cmd = request.POST['cmd']
            if cmd == 'add_partition':
                partition_name = request.POST['partition_name']
                _ = database_api.create_partition(partition_name)
            elif cmd == 'add_item':
                partition = request.POST['partition']
                read_groups = request.POST.getlist('read_groups[]')
                write_groups = request.POST.getlist('write_groups[]')
                _ = database_api.create_item(partition, {}, read_groups, write_groups)
            elif cmd == 'add_field':
                item_id = request.POST['item_id']
                field_name = request.POST['field_name']
                field_value = request.POST['field_value']
                field_type = request.POST['field_type']
                if field_type == 'S':
                    field_value = str(field_value)
                elif field_type == 'N':
                    field_value = Decimal(field_value)
                elif field_type == 'L':
                    field_value = list(field_value)
                _ = database_api.put_item_field(item_id, field_name, field_value)
            elif cmd == 'delete_partition':
                partition_name = request.POST['partition_name']
                _ = database_api.delete_partition(partition_name)
            elif cmd == 'delete_partitions':
                partitions = request.POST.getlist('partitions[]')
                _ = database_api.delete_partitions(partitions)
            elif cmd == 'get_items':
                partition = request.POST['partition']
                start_key = request.POST.get('start_key', None)
                result = database_api.get_items(partition, start_key=start_key)
                result = Util.encode_dict(result)
                return JsonResponse(result)
            elif cmd == 'get_item':
                item_id = request.POST['item_id']
                result = database_api.get_item(item_id)
                result = Util.encode_dict(result)
                return JsonResponse(result)
            elif cmd == 'delete_item':
                item_id = request.POST['item_id']
                result = database_api.delete_item(item_id)
                return JsonResponse(result)
            elif cmd == 'delete_items':
                item_ids = request.POST.getlist('item_ids[]')
                result = database_api.delete_items(item_ids)
                return JsonResponse(result)
            elif cmd == 'delete_field':
                item_id = request.POST['item_id']
                field_name = request.POST['field_name']
                result = database_api.put_item_field(item_id, field_name, None)
                return JsonResponse(result)
            elif cmd == 'delete_fields':
                field_names = request.POST.getlist('field_names[]')
                item_id = request.POST['item_id']
                for field_name in field_names:
                    result = database_api.put_item_field(item_id, field_name, None)
                return JsonResponse(result)
            elif cmd == 'get_item_count':
                partition = request.POST['partition']
                result = database_api.get_item_count(partition)
                result = Util.encode_dict(result)
                return JsonResponse(result)
            elif cmd == 'query_items':
                partition = request.POST['partition']
                query = request.POST['query']
                start_key = request.POST.get('start_key', None)
                query = json.loads(query)
                instructions = query['instructions']
                result = database_api.query_items(partition, instructions, start_key)
                return JsonResponse(result)
            elif cmd == 'get_policy_code':
                partition_to_apply = request.POST.get('partition_to_apply')
                mode = request.POST.get('mode')
                result = database_api.get_policy_code(partition_to_apply, mode)
                return JsonResponse(result)
            elif cmd == 'put_policy':
                partition_to_apply = request.POST.get('partition_to_apply')
                mode = request.POST.get('mode')
                code = request.POST.get('code')
                result = database_api.put_policy(partition_to_apply, mode, code)
                return JsonResponse(result)

        return redirect(request.path_info)  # Redirect back
