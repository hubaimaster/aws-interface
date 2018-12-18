from dashboard.views.view import DashboardView
from django.shortcuts import render, HttpResponse
from django.views.generic import View


class Auth(View, DashboardView):

    def get(self, request):
        context = {}
        return render(request, 'dashboard/auth.html', context=context)

