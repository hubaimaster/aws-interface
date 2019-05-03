
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.views.utils import Util, page_manage


class AccessKey(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        return render(request, 'dashboard/accesskey.html', context=context)

    @page_manage
    def post(self, request):
        password = request.POST['password']
        access_key = request.POST['access_key']
        secret_key = request.POST['secret_key']

        if not request.user.check_password(password):
            Util.add_alert(request, '비밀번호가 틀렸습니다.')
            return redirect('apps')

        if not Util.is_valid_access_key(access_key, secret_key):
            Util.add_alert(request, '유효한 AccessKey 를 입력해주세요.')
            return redirect('apps')

        request.user.set_aws_credentials(password, access_key, secret_key)
        request.user.save()

        credentials = dict()
        credentials['access_key'] = request.user.get_aws_access_key(password)
        credentials['secret_key'] = request.user.get_aws_secret_key(password)
        Util.reset_credentials(request, credentials)
        Util.add_alert(request, 'AccessKey 를 변경하였습니다.')
        return redirect('apps')

