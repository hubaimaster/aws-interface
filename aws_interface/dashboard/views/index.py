
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.views.utils import page_manage


class Index(LoginRequiredMixin, View):
    redirect_field_name = 'next'

    @page_manage
    def get(self, request):
        return redirect('apps')
