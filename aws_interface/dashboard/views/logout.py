from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.views.generic import View


class Logout(View, DashboardView):

    def get(self, request):
        self.set_login(request, False)
        return redirect('index')

