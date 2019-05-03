
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.views.utils import Util, page_manage


class Logout(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        Util.reset_credentials(request)
        logout(request)
        return redirect('index')
