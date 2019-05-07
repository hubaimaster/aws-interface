
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.views.utils import Util, page_manage
from core.adapter.django import DjangoAdapter


class Logic(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_auth() as auth_api:
            context['user_groups'] = auth_api.get_user_groups()['groups']
        return render(request, 'dashboard/app/logic.html', context=context)
