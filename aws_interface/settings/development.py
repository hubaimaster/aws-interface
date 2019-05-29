from .base import *

DEBUG = True

DB_NAME = secrets_base['DB_NAME']

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}
