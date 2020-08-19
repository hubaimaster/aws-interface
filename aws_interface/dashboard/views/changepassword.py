
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.views.utils import Util, page_manage


class ChangePassword(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        context['email'] = request.user.email
        return render(request, 'dashboard/changepassword.html', context=context)

    @page_manage
    def post(self, request):
        password = request.POST['password']
        new_password = request.POST['new_password']

        credentials = request.user.get_credentials(password)
        if not request.user.check_password(password):
            Util.add_alert(request, '비밀번호가 틀렸습니다.')
            return redirect('apps')

        request.user.set_password(new_password)
        request.user.save()

        request.user.set_credentials(new_password, credentials)
        request.user.save()

        credentials = request.user.get_credentials(new_password)
        Util.reset_credentials(request, credentials)
        Util.add_alert(request, '비밀번호를 변경하였습니다.')
        return redirect('apps')

