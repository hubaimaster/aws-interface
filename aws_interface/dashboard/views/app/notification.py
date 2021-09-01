
from core.adapter.django import DjangoAdapter
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from dashboard.views.utils import Util, page_manage
from django.template import loader


class Notification(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api, adapter.open_api_notification() as notification:
            context['slack_webhooks'] = notification.get_slack_webhooks(None)

        return render(request, 'dashboard/app/notification.html', context=context)

    def post(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id
        cmd = request.POST.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_notification() as notification:
            if cmd == 'get_email_provider_rows':
                start_key = request.POST.get('start_key', None)
                result = notification.get_email_providers(start_key)
                template = loader.get_template('dashboard/app/component/email_provider_table_row.html')
                items = result.get('items', [])
                end_key = result.get('end_key', None)
                context = {
                    'items': items,
                }
                result = {
                    'rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)
            elif cmd == 'get_slack_webhook_rows':
                start_key = request.POST.get('start_key', None)
                result = notification.get_slack_webhooks(start_key)
                template = loader.get_template('dashboard/app/component/slack_webhook_table_row.html')
                items = result.get('items', [])
                end_key = result.get('end_key', None)
                context = {
                    'items': items,
                }
                result = {
                    'rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)

            elif cmd == 'get_system_notification_rows':
                start_key = request.POST.get('start_key', None)
                result = notification.get_system_notifications(start_key)
                template = loader.get_template('dashboard/app/component/system_notification_table_row.html')
                items = result.get('items', [])
                end_key = result.get('end_key', None)
                context = {
                    'items': items,
                }
                result = {
                    'rows': template.render(context, request),
                    'end_key': end_key
                }
                return JsonResponse(result)

            elif cmd == 'create_email_provider':
                name = request.POST.get('email-provider-name')
                description = request.POST.get('email-provider-description')
                url = request.POST.get('email-provider-url')
                port = request.POST.get('email-provider-port')
                email = request.POST.get('email-provider-email')
                password = request.POST.get('email-provider-password')
                result = notification.create_email_provider(name, description, url, port, email, password)
                return JsonResponse(result)
            elif cmd == 'send_sms':
                phone_number = request.POST.get('sms-phone-number')
                message = request.POST.get('sms-message')
                result = notification.send_sms(message, phone_number)
                return JsonResponse(result)
            elif cmd == 'create_slack_webhook':
                name = request.POST.get('name')
                url = request.POST.get('url')
                result = notification.create_slack_webhook(name, url)
                return JsonResponse(result)
            elif cmd == 'delete_slack_webhook':
                name = request.POST.get('name')
                result = notification.delete_slack_webhook(name)
                return JsonResponse(result)
            elif cmd == 'get_slack_webhooks':
                start_key = request.POST.get('start_key')
                result = notification.get_slack_webhooks(start_key)
                return JsonResponse(result)
            elif cmd == 'send_slack_message':
                slack_webhook_name = request.POST.get('slack_webhook_name')
                text = request.POST.get('text')
                username = request.POST.get('username')
                icon_url = request.POST.get('icon_url')
                icon_emoji = request.POST.get('icon_emoji')
                channel = request.POST.get('channel')
                result = notification.send_slack_message(slack_webhook_name, text, username, icon_url, icon_emoji, channel)
                return JsonResponse(result)

            elif cmd == 'create_system_notification':
                slack_webhook_name = request.POST.get('slack_webhook_name')
                result = notification.create_system_notification(slack_webhook_name)
                return JsonResponse(result)
            elif cmd == 'delete_system_notification':
                system_notification_id = request.POST.get('system_notification_id')
                result = notification.delete_system_notification(system_notification_id)
                return JsonResponse(result)
            elif cmd == 'delete_email_provider':
                name = request.POST.get('name')
                result = notification.delete_email_provider(name)
                return JsonResponse(result)


        return redirect(request.path_info)  # Redirect back
