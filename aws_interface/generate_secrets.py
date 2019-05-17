import os
from os.path import dirname as _
import random
import json


if __name__ == '__main__':
    base_dir = _(os.path.abspath(__file__))
    secret_dir = os.path.join(base_dir, 'secret')
    os.makedirs(secret_dir, exist_ok=True)

    data = dict()
    data['SECRET_KEY'] = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
                                  for _ in range(50)])

    data['ADMIN_EMAIL'] = input('ADMIN_EMAIL: ')
    data['ADMIN_PASSWORD'] = input('ADMIN_PASSWORD: ')

    DB_ENGINE = input('DB_ENGINE (mysql, sqlite3) : ')
    data["DB_ENGINE"] = "django.db.backends.{}".format(DB_ENGINE)
    print('Using DB_ENGINE as {}'.format(data["DB_ENGINE"]))

    if DB_ENGINE == 'sqlite3':
        data["DB_NAME"] = input('DB_NAME (ex: db.sqlite3):')
    else:
        data["DB_NAME"] = input('DB_NAME: ')
        data["DB_USER"] = input('DB_USER: ')
        data["DB_PASSWORD"] = input('DB_PASSWORD: ')
        data["DB_HOST"] = input('DB_HOST: ')
        data["DB_PORT"] = input('DB_PORT: ')

    data["AWS_ACCESS_KEY"] = input('AWS_ACCESS_KEY: ')
    data["AWS_SECRET_KEY"] = input('AWS_SECRET_KEY: ')

    base_json = os.path.join(secret_dir, 'base.json')
    with open(base_json, 'w') as f:
        json.dump(data, f)

