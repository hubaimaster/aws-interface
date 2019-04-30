
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.views.utils import Util, page_manage

from core.adapter.django import DjangoAdapter


class Auth(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as api:
            context['user_groups'] = api.get_user_groups()
            context['user_count'] = api.get_user_count()
            context['session_count'] = api.get_session_count()
            context['users'] = api.get_users()
            context['sessions'] = api.get_sessions()
            context['email_login'] = api.get_email_login()
            context['guest_login'] = api.get_guest_login()
        return render(request, 'dashboard/app/auth.html', context=context)

    @page_manage
    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as api:
            cmd = request.POST['cmd']
            # Recipe
            if cmd == 'delete_group':
                name = request.POST['group_name']
                succeed = api.delete_user_group(name)
                if not succeed:
                    Util.add_alert(request, '시스템 그룹은 삭제할 수 없습니다.')
            elif cmd == 'put_group':
                name = request.POST['group_name']
                description = request.POST['group_description']
                api.put_user_group(name, description)
            elif cmd == 'set_email_login':
                default_group = request.POST['email_default_group']
                enabled = request.POST['email_enabled']
                if enabled == 'true':
                    enabled = True
                else:
                    enabled = False
                api.set_email_login(enabled, default_group)
            elif cmd == 'set_guest_login':
                default_group = request.POST['guest_default_group']
                enabled = request.POST['guest_enabled']
                if enabled == 'true':
                    enabled = True
                else:
                    enabled = False
                api.set_guest_login(enabled, default_group)

            # Service
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

        return redirect(request.path_info)  # Redirect back

