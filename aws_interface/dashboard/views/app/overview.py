
from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.adapter.django import DjangoAdapter
from dashboard.views.utils import Util, page_manage
from dashboard.models import App
import os


class Overview(LoginRequiredMixin, View):
    @page_manage
    def get(self, request, app_id):
        cmd = request.GET.get('cmd', None)
        adapter = DjangoAdapter(app_id, request)
        if cmd == 'download_sdk':
            sdk_bin = adapter.generate_sdk('python3')
            if sdk_bin is None:
                Util.add_alert(request, 'API 를 초기화 하고 있습니다. 상황에 따라 최대 3분 정도 소요될 수 있습니다.')
                return redirect(request.path_info)

            response = HttpResponse(sdk_bin, content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename('AWS Interface SDK.zip')
            return response
        else:
            context = Util.get_context(request)
            context['app_id'] = app_id
            app = App.objects.get(id=app_id, user=request.user)
            context['app_name'] = app.name
            return render(request, 'dashboard/app/overview.html', context=context)
