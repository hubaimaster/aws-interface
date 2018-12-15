from time import time
from django.shortcuts import render
from django.shortcuts import HttpResponse, redirect

from dashboard.models import User
import json
# Create your views here.


def pop_alert(request):
    alert = request.session.get('alert', None)
    request.session['alert'] = None
    return alert


def add_alert(request, alert):
    request.session['alert'] = alert


def index(request):
    is_loign = request.session.get('is_login', False)
    if is_loign:
        return overview(request)
    else:
        return login(request)


def apps(request):
    context = {}
    return render(request, 'dashboard/apps.html', context=context)


def login(request):
    if request.method == 'POST':
        return
    elif request.method == 'GET':
        context = {}
        return render(request, 'dashboard/login.html', context=context)


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        aws_access_key = request.POST['access_key']
        aws_secret_key = request.POST['secret_key']
        users = User.objects.filter(email=email)
        if len(users) > 0:
            add_alert(request, '이미 계정이 존재합니다.')
            return redirect('register')
        elif len(password) < 7:
            add_alert(request, '비밀번호는 7자 이상입니다.')
            return redirect('register')
        else:
            User.create(email, password, aws_access_key, aws_secret_key)
            add_alert(request, '회원가입에 성공하였습니다.')
            return redirect('index')

    elif request.method == 'GET':
        context = dict()
        context['alert'] = pop_alert(request)
        return render(request, 'dashboard/register.html', context=context)


def overview(request):
    context = {}
    return render(request, 'dashboard/overview.html', context=context)
