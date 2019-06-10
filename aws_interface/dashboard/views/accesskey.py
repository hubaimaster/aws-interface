
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.views.utils import Util, page_manage


class AccessKey(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        context['email'] = request.user.email
        return render(request, 'dashboard/accesskey.html', context=context)

    @page_manage
    def post(self, request):
        password = request.POST['password']
        vendor = request.POST['vendor']
        if vendor == 'aws':
            access_key = request.POST['aws_access_key']
            secret_key = request.POST['aws_secret_key']
            region = request.POST['aws_region']
            credential = {
                'access_key': access_key,
                'secret_key': secret_key,
                'region': region
            }

            if not request.user.check_password(password):
                Util.add_alert(request, '비밀번호가 틀렸습니다.')
                return redirect('apps')

            if not Util.is_valid_access_key(access_key, secret_key):
                Util.add_alert(request, '올바른 백엔드 인증 정보를 입력해주세요.')
                return redirect('apps')

            request.user.set_credential(password, vendor, credential)
            request.user.save()

            credentials = request.user.get_credentials(password)
            Util.reset_credentials(request, credentials)
            Util.add_alert(request, '백엔드 인증 정보를 변경하였습니다.')
            return redirect('apps')

