from django.shortcuts import render
from django.shortcuts import HttpResponse
# Create your views here.


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
    context = {}
    return render(request, 'dashboard/login.html', context=context)


def register(request):
    context = {}
    return render(request, 'dashboard/register.html', context=context)


def overview(request):
    context = {}
    return render(request, 'dashboard/overview.html', context=context)