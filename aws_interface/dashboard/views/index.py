from dashboard.views.view import DashboardView
from django.shortcuts import redirect
from django.views.generic import View


class Index(View, DashboardView):
    def get(self, request):
        if self.is_login(request):
            return redirect('apps')
        else:
            return redirect('login')