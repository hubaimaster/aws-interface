import os
from os.path import dirname as _
import random
import json


if __name__ == '__main__':
    base_dir = _(_(os.path.abspath(__file__)))
    secret_dir = os.path.join(base_dir, 'secret')
    os.makedirs(secret_dir, exist_ok=True)

    data = dict()
    data['SECRET_KEY'] = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
                                  for _ in range(50)])

    base_json = os.path.join(secret_dir, 'base.json')
    with open(base_json, 'w') as f:
        json.dump(data, f)
