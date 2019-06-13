"""Django - Dashboard application view of Auth service
"""
from decimal import Decimal
from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template import loader
from dashboard.views.utils import Util, page_manage
from core.adapter.django import DjangoAdapter
from concurrent.futures import ThreadPoolExecutor


class Auth(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as api:
            context['user_groups'] = api.get_user_groups()['groups']
            context['user_count'] = api.get_user_count()
            context['session_count'] = api.get_session_count()
            context['users'] = api.get_users()
            context['visible_user_fields'] = ['id', 'creation_date', 'email', 'groups']
            context['none_extra_fields'] = ['id', 'creation_date', 'email', 'groups',
                                            'password_hash', 'salt', 'partition', 'login_method']
            context['sessions'] = api.get_sessions()
            context['email_login'] = api.get_email_login()['item']
            context['guest_login'] = api.get_guest_login()['item']
            context['all_permissions'] = api.get_all_permissions()['permissions']

        return render(request, 'dashboard/app/auth.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as api:
            cmd = request.POST['cmd']

            if cmd == 'delete_group':
                name = request.POST['group_name']
                error = api.delete_user_group(name).get('error', None)
                if error:
                    Util.add_alert(request, '{}: {}'.format(error['code'], error['message']))
            elif cmd == 'put_group':
                name = request.POST['group_name']
                description = request.POST['group_description']
                api.put_user_group(name, description)
            elif cmd == 'set_email_login':
                default_group = request.POST['default_group_name']
                enabled = request.POST['enabled']
                if enabled == 'true':
                    enabled = True
                else:
                    enabled = False
                api.set_email_login(enabled, default_group)
            elif cmd == 'set_guest_login':
                default_group = request.POST['default_group_name']
                enabled = request.POST['enabled']
                if enabled == 'true':
                    enabled = True
                else:
                    enabled = False
                api.set_guest_login(enabled, default_group)

            elif cmd == 'put_user':
                email = request.POST['user_email']
                password = request.POST['user_password']
                api.create_user(email, password, {})
            elif cmd == 'delete_user':
                user_id = request.POST['user_id']
                api.delete_user(user_id)
            elif cmd == 'delete_sessions':
                session_ids = request.POST.getlist('session_ids[]')
                api.delete_sessions(session_ids)
            elif cmd == 'delete_users':
                user_ids = request.POST.getlist('user_ids[]')
                api.delete_users(user_ids)
            elif cmd == 'detach_group_permission':
                group_name = request.POST.get('group_name')
                permission = request.POST.get('permission')
                api.detach_group_permission(group_name, permission)
            elif cmd == 'attach_group_permission':
                group_name = request.POST.get('group_name')
                permission = request.POST.get('permission')
                api.attach_group_permission(group_name, permission)
            elif cmd == 'set_users':
                user_ids = request.POST.getlist('user_ids[]')
                field_name = request.POST.get('field_name')
                field_type = request.POST.get('field_type')
                field_value = request.POST.get('field_value', None)
                if field_type == 'S':
                    field_value = str(field_value)
                elif field_type == 'N':
                    field_value = Decimal(field_value)
                with ThreadPoolExecutor(max_workers=32) as exc:
                    for user_id in user_ids:
                        exc.submit(api.set_user, user_id, field_name, field_value)
            elif cmd == 'attach_user_group':
                user_id = request.POST.get('user_id')
                group_name = request.POST.get('group_name')
                api.attach_user_group(user_id, group_name)
            elif cmd == 'detach_user_group':
                user_id = request.POST.get('user_id')
                group_name = request.POST.get('group_name')
                api.detach_user_group(user_id, group_name)
            elif cmd == 'get_sessions':
                start_key = request.POST.get('start_key', None)
                result = api.get_sessions(start_key=start_key, limit=30)
                return JsonResponse(result)
            elif cmd == 'get_users':
                start_key = request.POST.get('start_key', None, limit=30)
                result = api.get_users(start_key=start_key)
                return JsonResponse(result)
            elif cmd == 'get_user_rows':
                start_key = request.POST.get('start_key', None)
                result = self._get_user_rows(request, app_id, start_key)
                return JsonResponse(result)

        return redirect(request.path_info)  # Redirect back

    def _get_user_rows(self, request, app_id, start_key=None):
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as api:
            result = api.get_users(start_key, limit=30)
            users = result['items']
            end_key = result.get('end_key')
            user_groups = api.get_user_groups()['groups']
            visible_user_fields = ['id', 'creation_date', 'email', 'groups']
            none_extra_fields = ['id', 'creation_date', 'email', 'groups',
                                 'password_hash', 'salt', 'partition', 'login_method']
            template = loader.get_template('dashboard/app/component/auth_user_table_row.html')
            context = {
                'users': users,
                'user_groups': user_groups,
                'visible_user_fields': visible_user_fields,
                'none_extra_fields': none_extra_fields,
            }
            return {
                'user_rows': template.render(context, request),
                'end_key': end_key
            }
