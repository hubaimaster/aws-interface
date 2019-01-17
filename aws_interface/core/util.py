import boto3
from datetime import date


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session


def get_current_date():
    today = date.today()
    return today


def get_current_month_date():
    today = date.today()
    datem = date(today.year, today.month, 1)
    return datem