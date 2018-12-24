from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.views.generic import View


class Apps(View, DashboardView):

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'dashboard/apps.html', context=context)

    def post(self, request): #Create app
        name = request.POST['name']
        self.add_alert(request, '새로운 어플리케이션이 생성되었습니다:' + name)
        return redirect('apps')

