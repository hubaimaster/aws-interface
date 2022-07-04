from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from core.adapter.django import DjangoAdapter
from dashboard.views.utils import Util, page_manage
from decimal import Decimal
import json


class FastDatabase(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        # allocate_resource_in_background(adapter)
        with adapter.open_api_auth() as auth_api, adapter.open_api_fast_database() as fast_database_api:
            partitions = fast_database_api.get_partitions().get('partitions', [])
            for partition in partitions:
                partition['name'] = partition['_partition_name']
            context['user_groups'] = auth_api.get_user_groups()['groups']
            context['partitions'] = partitions
        return render(request, 'dashboard/app/fast_database.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_fast_database() as database_api:
            cmd = request.POST['cmd']
            if cmd == 'add_partition':
                partition_name = request.POST['partition_name']
                pk_group = request.POST['pk_group']
                pk_field = request.POST['pk_field']

                sk_group = request.POST['sk_group']
                sk_field = request.POST['sk_field']

                post_sk_fields = request.POST.getlist('post_sk_fields[]')
                use_random_sk_postfix = request.POST['use_random_sk_postfix']
                if not isinstance(use_random_sk_postfix, bool):
                    if str(use_random_sk_postfix).lower() == 'true':
                        use_random_sk_postfix = True
                    else:
                        use_random_sk_postfix = False

                result = database_api.create_partition(
                    partition_name,
                    pk_group, pk_field,
                    sk_group, sk_field,
                    post_sk_fields, use_random_sk_postfix
                )
                return JsonResponse(result)

            elif cmd == 'add_item':
                partition = request.POST['partition']
                _ = database_api.create_item(partition, {})

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
            elif cmd == 'get_item':
                item_id = request.POST['item_id']
                result = database_api.get_item(item_id)
                result = Util.encode_dict(result)
                return JsonResponse(result)
            elif cmd == 'delete_item':
                partition = request.POST['partition']
                item_id = request.POST['item_id']
                result = database_api.delete_item(partition, item_id)
                return JsonResponse(result)
            elif cmd == 'delete_items':
                partition = request.POST['partition']
                item_ids = request.POST.getlist('item_ids[]')
                result = database_api.delete_items(partition, item_ids)
                return JsonResponse(result)

            elif cmd == 'query_items':
                pk_group = request.POST['pk_group']
                pk_field = request.POST['pk_field']
                pk_value = request.POST['pk_value']

                sort_condition = request.POST.get('sort_condition', None)
                sk_group = request.POST.get('sk_group', None)
                partition = request.POST.get('partition', None)
                sk_field = request.POST.get('sk_field', None)
                sk_value = request.POST.get('sk_value', None)

                sk_second_value = request.POST.get('sk_second_value', None)

                filters = request.POST.getlist('filters[]')
                start_key = request.POST.get('start_key', None)
                limit = request.POST.get('limit', 100)
                reverse = request.POST.get('reverse', False)

                consistent_read = request.POST.get('consistent_read', False)
                projection_keys = request.POST.get('projection_keys', None)
                index_name = request.POST.get('index_name', None)

                filters = json.loads(filters)
                result = database_api.query_items(
                    pk_group, pk_field, pk_value,
                    sort_condition=sort_condition,
                    sk_group=sk_group, partition=partition, sk_field=sk_field, sk_value=sk_value,
                    sk_second_value=sk_second_value,
                    filters=filters, start_key=start_key, limit=limit, reverse=reverse,
                    consistent_read=consistent_read, projection_keys=projection_keys, index_name=index_name
                )
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
