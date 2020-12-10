#!/usr/bin/env bash
export PYTHONUNBUFFERED=1;
export DJANGO_SETTINGS_MODULE=settings.production;

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsu
python manage.py runserver 0.0.0.0:8000