"""aws_interface URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from dashboard.views import *


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Index.as_view(), name='index'),

    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('apps/', Apps.as_view(), name='apps'),
    path('logout/', Logout.as_view(), name='logout'),
    path('account/', Account.as_view(), name='account'),

    path('overview/<app_id>', Overview.as_view(), name='overview'),
    path('bill/<app_id>', Bill.as_view(), name='bill'),
    path('auth/<app_id>', Auth.as_view(), name='auth'),
    path('database/<app_id>', Database.as_view(), name='database'),
    path('storage/<app_id>', Storage.as_view(), name='storage'),
]
