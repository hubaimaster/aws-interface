
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.adapter.django import DjangoAdapter
from dashboard.views.utils import Util, page_manage


class Bill(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        cache_key = 'bill-context-' + app_id
        context = Util.get_cache(request, cache_key)
        if context:
            return render(request, 'dashboard/app/bill.html', context=context)

        context = Util.get_context(request)
        context['app_id'] = app_id

        adapter = DjangoAdapter(app_id, request)
        with adapter.open_api_bill() as api:
            context['cost'] = api.get_current_cost()
            context['usages'] = api.get_current_usage_costs()
        Util.set_cache(request, cache_key, context)
        return render(request, 'dashboard/app/bill.html', context=context)

