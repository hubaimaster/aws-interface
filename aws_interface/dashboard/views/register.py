from dashboard.views.view import DashboardView
from django.shortcuts import render, HttpResponse, redirect
from dashboard.models import User
from django.views.generic import View


class Register(View, DashboardView):

    def get(self, request):
        context = self.get_context(request)
        return render(request, 'dashboard/register.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        aws_access_key = request.POST['access_key']
        aws_secret_key = request.POST['secret_key']
        users = User.objects.filter(email=email)
        if len(users) > 0:
            self.add_alert(request, '이미 계정이 존재합니다.')
            return redirect('register')
        elif len(password) < 7:
            self.add_alert(request, '비밀번호는 7자 이상입니다.')
            return redirect('register')
        else:
            User.create(email, password, aws_access_key, aws_secret_key)
            self.add_alert(request, '회원가입에 성공하였습니다.')
            return redirect('index')


