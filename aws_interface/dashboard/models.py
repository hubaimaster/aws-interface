
from contextlib import contextmanager
import uuid
from django.db import models
from dashboard.security.crypto import AESCipher
from django.contrib.auth.models import AbstractUser, BaseUserManager
import cloud.shortuuid as shortuuid
import core.api
import json


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        from dashboard.security.crypto import Salt
        if not email:
            raise ValueError('The given email must be set')

        credentials = extra_fields.pop('credentials', None)

        email = self.normalize_email(email)
        user = self.model(username=email, email=email, **extra_fields)
        user.salt = Salt.get_salt(32)
        user.set_password(password)

        if credentials is not None:
            user.set_credentials(password, credentials)
        else:
            assert(credentials is None)

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
    c_credentials = models.TextField()

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

    def set_credential(self, raw_password, vendor, credential):
        assert (self.check_password(raw_password))
        if self.c_credentials:
            credentials = self.decrypt(raw_password, self.c_credentials)
            credentials = json.loads(credentials)
        else:
            credentials = dict()
        credentials[vendor] = credential
        self.c_credentials = self.encrypt(raw_password, credentials)

    def get_credential(self, raw_password, vendor):
        assert (self.check_password(raw_password))
        return self.decrypt(raw_password, self.c_credentials).get(vendor, None)

    def set_credentials(self, raw_password, credentials):
        assert (self.check_password(raw_password))
        credentials = json.dumps(credentials)
        self.c_credentials = self.encrypt(raw_password, credentials)

    def get_credentials(self, raw_password):
        assert (self.check_password(raw_password))
        credentials = self.decrypt(raw_password, self.c_credentials)
        credentials = json.loads(credentials)
        return credentials


class App(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=shortuuid.uuid, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    name = models.CharField(max_length=255, blank=False, unique=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    vendor = models.CharField(max_length=255, default='aws')

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=shortuuid.uuid, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    name = models.CharField(max_length=255, editable=False)
    json_string = models.TextField(default='')
    app = models.ForeignKey(App, null=True, on_delete=models.CASCADE)  # should not be NULL from now on
    need_deploy = models.BooleanField(default=True)

    def __str__(self):
        return self.name.title()

    def get_api(self, vendor, credential):
        api_cls = core.api.api_dict[self.name]
        return api_cls(vendor, credential, self.app.id, self.json_string)

    def save_recipe(self, api: core.api.API):
        self.json_string = api.get_recipe_controller().to_json()
        self.save()

    def set_need_deploy(self, need_deploy):
        self.need_deploy = need_deploy
        self.save()

    @contextmanager
    def api(self, credential):
        """
        You can do this:
            with recipe.api() as api:
                use(api)
        Instead of this:
            api = recipe.api()
            use(api)
            recipe.save_recipe(api)
        :param vendor:
        :param credential:
        :return:
        """
        api = self.get_api(self.app.vendor, credential)
        prev_json_string = self.json_string
        yield api
        if api.get_recipe_controller().to_json() != prev_json_string:
            self.set_need_deploy(True)
        self.save_recipe(api)
