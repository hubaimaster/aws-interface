
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import IntegrityError

from dashboard.models import *
from dashboard.views.utils import Util, page_manage
from core.adapter.django import DjangoAdapter


class Apps(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        try:
            apps = App.objects.filter(user=request.user)
            apps = [{'id': app.id, 'creation_date': app.creation_date, 'name': app.name} for app in apps]
            context['apps'] = apps
        except ObjectDoesNotExist:
            context['apps'] = []
        return render(request, 'dashboard/apps.html', context=context)

    @page_manage
    def post(self, request):
        cmd = request.POST.get('cmd', None)
        if cmd == 'create_app':
            self.create_app(request)
            return redirect('apps')
        elif cmd == 'remove_app':
            app_id = request.POST['app_id']

            try:
                app = App.objects.get(id=app_id, user=request.user)
                adapter = DjangoAdapter(app_id, request)
                adapter.terminate_resource()
                app.delete()
                Util.add_alert(request, 'Application removed')
            except IntegrityError as ex:
                print(ex)
                Util.add_alert(request, 'Failed to remove application')
            return redirect('apps')

    @classmethod
    def create_app(cls, request):
        name = request.POST['name']
        if not name or len(name) < 3:
            Util.add_alert(request, '이름은 3글자 이상입니다')
            return redirect('apps')
        user = request.user
        app = App.objects.filter(user=request.user, name=name)
        if app:
            Util.add_alert(request, '같은 이름의 어플리케이션이 존재합니다')
            return redirect('apps')
        app = App()
        app.name = name
        app.user = user
        app.save()
        Util.add_alert(request, '새로운 어플리케이션이 생성되었습니다')
