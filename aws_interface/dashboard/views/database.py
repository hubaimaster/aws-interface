from dashboard.views.view import DashboardView
from django.shortcuts import render, HttpResponse
from django.views.generic import View


class Database(View, DashboardView):

    def get(self, request):
        context = {}
        return render(request, 'dashboard/database.html', context=context)

