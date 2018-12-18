
from dashboard.views.view import DashboardView
from django.shortcuts import render, HttpResponse
from django.views.generic import View


class Storage(View, DashboardView):

    def get(self, request):
        context = {}
        return render(request, 'dashboard/storage.html', context=context)

