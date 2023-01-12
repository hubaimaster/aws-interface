from .base import Adapter
from dashboard.models import App


class DjangoAdapter(Adapter):
    def __init__(self, app_id, request):
        self.app = App.objects.get(id=app_id)
        # 여기서 앱 별로 region 설정이 가능하게 변경
        self.credential = request.session.get('credentials', {})

    def _get_app_id(self):
        return self.app.id

    def _get_credential(self):
        # app 에 있는 region 정보가 있을경우 업데이트해서 주기
        credential = self.credential.copy()
        if credential and self.app.region:
            if self.app.vendor == 'aws' and credential['aws']:
                credential['aws'] = credential['aws'].copy()
                credential['aws']['region'] = self.app.region
        return credential

    def _get_vendor(self):
        return self.app.vendor
