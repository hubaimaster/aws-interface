from dashboard.views.view import DashboardView
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin


class Index(LoginRequiredMixin, View, DashboardView):
    redirect_field_name = 'next'

    def get(self, request):
        return redirect('apps')
