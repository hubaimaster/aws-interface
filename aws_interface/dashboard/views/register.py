import warnings

from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import get_user_model
from dashboard.views.utils import Util, page_manage


class Register(View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/register.html', context=context)

    @page_manage
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        vendor = request.POST['vendor']

        aws_access_key = request.POST['aws_access_key']
        aws_secret_key = request.POST['aws_secret_key']
        aws_region = request.POST['aws_region']

        normalized_email = get_user_model().objects.normalize_email(email)
        users = get_user_model().objects.all().filter(email=normalized_email)
        if len(users) > 0:
            if len(users) > 1:
                warnings.warn('there are {} users with email {}'.format(len(users), email))

            Util.add_alert(request, '이미 계정이 존재합니다.')
            return redirect('register')
        elif len(password) < 7:
            Util.add_alert(request, '비밀번호는 7자 이상입니다.')
            return redirect('register')
        elif not Util.is_valid_access_key(aws_access_key, aws_secret_key):
            Util.add_alert(request, '유효한 AccessKey 를 입력해주세요.')
            return redirect('register')
        else:
            credentials = {}
            if vendor == 'aws':
                credentials['aws'] = {
                    'access_key': aws_access_key,
                    'secret_key': aws_secret_key,
                    'region': aws_region,
                }
            get_user_model().objects.create_user(
                email, password,
                credentials=credentials,
            )
            Util.add_alert(request, '회원가입에 성공하였습니다.')
            return redirect('index')
