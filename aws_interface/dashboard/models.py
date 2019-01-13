from django.db import models
import uuid
# Create your models here.


class User(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    email = models.CharField(max_length=255, blank=False, unique=True)
    password_hash = models.CharField(max_length=255, blank=False)
    c_aws_access_key = models.CharField(max_length=255)
    c_aws_secret_key = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)

    @classmethod
    def create(cls, email, password, aws_access_key, aws_secret_key):
        from dashboard.security.crypto import AESCipher, Salt
        salt = Salt.get_salt(32)
        aes = AESCipher(password + salt)
        password_hash = cls.get_password_hash(password, salt)
        c_aws_access_key = aes.encrypt(aws_access_key)
        c_aws_secret_key = aes.encrypt(aws_secret_key)

        user = User()
        user.email = email
        user.password_hash = password_hash
        user.c_aws_access_key = c_aws_access_key
        user.c_aws_secret_key = c_aws_secret_key
        user.salt = salt
        return user.save()

    @classmethod
    def get_password_hash(cls, password, salt):
        from dashboard.security.crypto import Hash
        password_hash = Hash.sha3_512(password + salt)
        return password_hash


class App(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=False, unique=True)


class Recipe(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    recipe_id = models.CharField(max_length=255)
    recipe_type = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    json_string = models.TextField()