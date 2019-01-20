from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import View
from django.conf import settings


class Login(View, DashboardView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = self.get_context(request)
            return render(request, 'dashboard/login.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)

        if user is None:
            self.add_alert(request, '로그인 정보가 틀렸습니다')
            return redirect('login')
        else:
            request.session['access_key'] = user.get_aws_access_key(password)
            request.session['secret_key'] = user.get_aws_secret_key(password)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
