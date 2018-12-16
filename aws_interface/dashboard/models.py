from django.db import models
import uuid
# Create your models here.


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    email = models.CharField(max_length=200, blank=False, unique=True)
    password_hash = models.CharField(max_length=512, blank=False)
    c_aws_access_key = models.CharField(max_length=512)
    c_aws_secret_key = models.CharField(max_length=512)
    salt = models.CharField(max_length=512)

    @classmethod
    def create(cls, email, password, aws_access_key, aws_secret_key):
        from dashboard.security.crypto import AESCipher, Hash, Salt
        salt = Salt.get_salt(32)
        aes = AESCipher(password + salt)
        password_hash = Hash.sha3_512(password + salt)
        c_aws_access_key = aes.encrypt(aws_access_key)
        c_aws_secret_key = aes.encrypt(aws_secret_key)

        user = User()
        user.email = email
        user.password_hash = password_hash
        user.c_aws_access_key = c_aws_access_key
        user.c_aws_secret_key = c_aws_secret_key
        user.salt = salt
        return user.save()
