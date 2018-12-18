
from dashboard.views.view import DashboardView
from django.shortcuts import render
from django.views.generic import View


class Overview(View, DashboardView):

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'dashboard/overview.html', context=context)

