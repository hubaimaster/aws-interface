from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.generic import View
import warnings


class Register(View, DashboardView):

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'dashboard/register.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        aws_access_key = request.POST['access_key']
        aws_secret_key = request.POST['secret_key']

        normalized_email = get_user_model().objects.normalize_email(email)
        users = get_user_model().objects.all().filter(email=normalized_email)
        if len(users) > 0:
            if len(users) > 1:
                warnings.warn('there are {} users with email {}'.format(len(users), email))

            self.add_alert(request, '이미 계정이 존재합니다.')
            return redirect('register')
        elif len(password) < 7:
            self.add_alert(request, '비밀번호는 7자 이상입니다.')
            return redirect('register')
        else:
            get_user_model().objects.create_user(
                email, password,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
            )
            self.add_alert(request, '회원가입에 성공하였습니다.')
            return redirect('index')
