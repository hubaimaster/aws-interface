from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate
from django.conf import settings
from dashboard.views.utils import Util, page_manage


class Login(View):
    @page_manage
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = Util.get_context(request)
            return render(request, 'dashboard/login.html', context=context)

    @page_manage
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)

        if user is None:
            Util.add_alert(request, '로그인 정보가 틀렸습니다')
            return redirect('login')
        else:
            credentials = user.get_credentials(password)
            Util.reset_credentials(request, credentials)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

