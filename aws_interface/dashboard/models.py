from django.db import models
from dashboard.security.crypto import AESCipher
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        from dashboard.security.crypto import Salt
        if not email:
            raise ValueError('The given email must be set')

        access_key = extra_fields.pop('aws_access_key')
        secret_key = extra_fields.pop('aws_secret_key')

        email = self.normalize_email(email)
        user = self.model(username=email, email=email, **extra_fields)
        user.salt = Salt.get_salt(32)
        user.set_password(password)

        if access_key is not None and secret_key is not None:
            user.set_aws_credentials(password, access_key, secret_key);
        else:
            assert(access_key is None and secret_key is None)

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    email = models.CharField(max_length=200, blank=False, unique=True)
    c_aws_access_key = models.CharField(max_length=256, null=True)
    c_aws_secret_key = models.CharField(max_length=256, null=True)
    salt = models.CharField(max_length=512)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = UserManager()

    # the following methods use raw_password, hence should only be
    # at login or registration

    def encrypt(self, raw_password, string):
        # uses raw_password, hence can only be done at login or registration
        from dashboard.security.crypto import AESCipher
        aes = AESCipher(raw_password + self.salt)
        assert (self.check_password(raw_password))
        return aes.encrypt(string)

    def decrypt(self, raw_password, string):
        aes = AESCipher(raw_password + self.salt)
        assert (self.check_password(raw_password))
        return aes.decrypt(string)

    def set_aws_credentials(self, raw_password, access_key, secret_key):
        assert (self.check_password(raw_password))
        self.c_aws_access_key = self.encrypt(raw_password, access_key)
        self.c_aws_secret_key = self.encrypt(raw_password, secret_key)

    def get_aws_access_key(self, raw_password):
        assert (self.check_password(raw_password))
        return self.decrypt(raw_password, self.c_aws_access_key)

    def get_aws_secret_key(self, raw_password):
        assert (self.check_password(raw_password))
        return self.decrypt(raw_password, self.c_aws_secret_key)


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