from django.core.management.base import BaseCommand
from dashboard.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('kchdully@gmail.com', 'kch1234')
