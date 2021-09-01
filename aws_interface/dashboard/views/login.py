from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate
from dashboard.models import OTPCode
from dashboard.views.utils import Util, page_manage
from django.conf import settings
import emails
import random
import string


TIMEOUT = 3

EMAIL_USER = getattr(settings, "EMAIL_USER", None)
EMAIL_PASSWORD = getattr(settings, "EMAIL_PASSWORD", None)


def send_email(email_from, email_to, title, content, host, port, user, password):
    message = emails.html(
        html=content,
        subject=title,
        mail_from=email_from,
    )

    resp = message.send(
        to=email_to,
        smtp={
            "host": host,
            "port": port,
            "timeout": TIMEOUT,
            "user": user,
            "password": password,
            "tls": True,
        },
    )
    return resp


def random_char(y):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(y))


class Login(View):
    def send_otp_email(self, email):
        code = random_char(8)
        send_email('system@aws-interface.com', email, 'aws-interface.com OTP Code', code,
                         'email-smtp.ap-northeast-2.amazonaws.com', 587,
                         EMAIL_USER, EMAIL_PASSWORD)
        # 25, 465 or 587
        otp_code = OTPCode()
        otp_code.email = email
        otp_code.code = code
        otp_code.save()

    def verify_otp_code(self, email, code):
        """
        OTP code 와 일치하는지 확인
        :param email:
        :param code:
        :return:
        """
        otp_codes = OTPCode.objects.filter(email=email)
        success = False
        if otp_codes:
            otp_code = otp_codes[0]
            if otp_code.code == code:
                success = True
        for otp_code in otp_codes:
            otp_code.delete()
        return success

    @page_manage
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = Util.get_context(request)
            Util.pop_value(request, context, 'otp_hidden', True)
            return render(request, 'dashboard/login.html', context=context)

    @page_manage
    def post(self, request):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        otp_code = request.POST.get('otp_code', None)
        if otp_code and password:
            email = request.session['email']
            if self.verify_otp_code(email, otp_code):
                user = authenticate(username=email, password=password)
                request.session['email'] = None
                if user is None:
                    Util.add_alert(request, '로그인 정보가 틀렸습니다.')
                    request.session['otp_hidden'] = True
                    return redirect('login')
                else:
                    credentials = user.get_credentials(password)
                    Util.reset_credentials(request, credentials)
                    login(request, user)
                    request.session['otp_hidden'] = True
                    return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                Util.add_alert(request, '인증번호가 틀렸습니다.')
                request.session['otp_hidden'] = True
                return redirect('login')
        elif email:
            self.send_otp_email(email)
            request.session['email'] = email
            Util.add_alert(request, '이메일로 인증번호가 전송되었습니다.')
            request.session['otp_hidden'] = False
            return redirect('login')
        else:
            Util.add_alert(request, '모든 정보를 입력헤주세요.')
            request.session['otp_hidden'] = False
            return redirect('login')
