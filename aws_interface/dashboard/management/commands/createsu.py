from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from dashboard.models import User
import os
import json
import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():

            base_dir = os.path.dirname(os.path.abspath(settings.__file__))
            secret_dir = os.path.join(base_dir, 'secret')
            secret_base_dir = os.path.join(secret_dir, 'base.json')

            try:
                secrets_base = json.load(open(secret_base_dir, 'rt'))
                admin_email = secrets_base.get('ADMIN_EMAIL', 'admin@awsi.com')
                admin_password = secrets_base.get('ADMIN_PASSWORD', 'admin1234')
            except FileNotFoundError:
                raise ImproperlyConfigured('Could not find secret file {}'.format(secret_base_dir))

            User.objects.create_superuser(admin_email, admin_password)
