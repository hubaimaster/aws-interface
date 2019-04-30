
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.models import *
from dashboard.views.utils import Util, page_manage


class Apps(LoginRequiredMixin, View):
    @page_manage
    def get(self, request):
        context = Util.get_context(request)
        try:
            apps = App.objects.filter(user_id=request.user.id)
            apps = [{'id': app.id, 'creation_date': app.creation_date, 'name': app.name} for app in apps]
            context['apps'] = apps
        except ObjectDoesNotExist:
            context['apps'] = []
        return render(request, 'dashboard/apps.html', context=context)

    @page_manage
    def post(self, request):
        cmd = request.POST.get('cmd', None)
        if cmd == 'create_app':
            Util.create_app(request)
            return redirect('apps')
        elif cmd == 'remove_app':
            app_id = request.POST['app_id']
            apps = App.objects.filter(id=app_id, user=request.user)
            if apps:
                app = apps[0]
                credentials = Util.get_credentials(request)
                Util.terminate_resource(credentials, app)
                Util.add_alert(request, 'Application removed')
            else:
                Util.add_alert(request, 'Failed to remove application')
            return redirect('apps')

