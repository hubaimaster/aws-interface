from dashboard.views.view import DashboardView
from django.shortcuts import render, redirect
from dashboard.models import User
from django.views.generic import View


class Login(View, DashboardView):

    def get(self, request):
        if self.is_login(request):
            return redirect('index')
        else:
            context = self.get_context(request)
            return render(request, 'dashboard/login.html', context=context)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            self.add_alert(request, '존재하지 않는 계정입니다')
            return redirect('login')
        else:
            salt = user.salt
            print('salt:', salt)
            password_hash = User.get_password_hash(password, salt)
            if user.password_hash == password_hash:
                self.set_login(request, True)
                return redirect('index')
            else:
                self.add_alert('비밀번호가 틀렸습니다')
                return redirect('index')