

class DashboardView:

    @classmethod
    def pop_alert(cls, request, context):
        alert = request.session.get('alert', None)
        request.session['alert'] = None
        context['alert'] = alert

    @classmethod
    def add_alert(cls, request, alert):
        request.session['alert'] = alert

    @classmethod
    def is_login(cls, request):
        return request.session.get('is_login', False)

    @classmethod
    def set_login(cls, request, is_login):
        request.session['is_login'] = is_login
