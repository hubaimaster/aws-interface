#!/usr/bin/python
# -*- coding: utf-8 -*-


import importlib
import time
import traceback
import io
from contextlib import redirect_stdout


# AWS Lambda handler [Stand Alone]
def main(event, context):
    start = time.time()
    params = event
    payload = params.get('payload', {})
    user = params.get('user', None)
    show_traceback = params.get('show_traceback', False)

    handler_name = params.get('handler', None)
    if not handler_name:
        raise NameError('Check <handler> params')

    std_str = io.StringIO()
    with redirect_stdout(std_str):
        try:
            handler_package = '.'.join(handler_name.split('.')[:-1])
            method_name = handler_name.split('.')[-1]
            module = importlib.import_module(handler_package)
            handler_method = getattr(module, method_name)
            response = handler_method(payload, user)
            stdout = std_str.getvalue()
            duration = time.time() - start
        except Exception as ex:
            stdout = std_str.getvalue()
            if show_traceback:
                error = f'Exception:{ex}\ntraceback:{traceback.format_exc()}'
            else:
                error = None
            duration = time.time() - start
            return {
                'response': None,
                'stdout': stdout,
                'error': error,
                'duration': duration,
            }

    response_body = {
        'response': response,
        'stdout': stdout,
        'duration': duration
    }
    return response_body
