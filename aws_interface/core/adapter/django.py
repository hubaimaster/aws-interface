from .base import Adapter
from dashboard.models import App


class DjangoAdapter(Adapter):
    def __init__(self, app_id, request):
        self.app = App.objects.get(id=app_id)
        self.credential = request.session.get('credentials', {})

    def _get_app_id(self):
        return self.app.id

    def _get_credential(self):
        return self.credential

    def _get_vendor(self):
        return self.app.vendor
