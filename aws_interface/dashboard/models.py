from django.db import models

# Create your models here.


class Person(models.User):
    id = models.UUIDField(primary_key=True)
    creation_date = models.DateTimeField()
    email = models.CharField(max_length=200, blank=False)
    password_s_hash = models.CharField(max_length=200, blank=False)
    c_aws_access_key = models.CharField(max_length=200, blank=False)
    c_aws_secret_key = models.CharField(max_length=200, blank=False)