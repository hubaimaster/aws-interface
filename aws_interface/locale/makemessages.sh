#!/usr/bin/env bash
cd ..
python3 manage.py makemessages -l ko --settings=settings.development
python3 manage.py makemessages -l en --settings=settings.development