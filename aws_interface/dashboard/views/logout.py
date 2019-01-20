from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.generic import View


class Logout(View, DashboardView):

    def get(self, request):
        request.session['access_key'] = None
        request.session['secret_key'] = None
        logout(request)
        return redirect('index')

