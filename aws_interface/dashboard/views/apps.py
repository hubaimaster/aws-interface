from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class Apps(View, DashboardView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'dashboard/apps.html', context=context)

    def post(self, request): #Create app
        name = request.POST['name']
        self.add_alert(request, '새로운 어플리케이션이 생성되었습니다:' + name)
        return redirect('apps')

