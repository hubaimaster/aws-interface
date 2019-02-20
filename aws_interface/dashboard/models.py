from django.db import models
from dashboard.security.crypto import AESCipher
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from contextlib import contextmanager
import cloud.shortuuid as shortuuid
from core import recipe_controller
import core.api


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        from dashboard.security.crypto import Salt
        if not email:
            raise ValueError('The given email must be set')

        access_key = extra_fields.pop('aws_access_key', None)
        secret_key = extra_fields.pop('aws_secret_key', None)

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
    id = models.CharField(max_length=255, primary_key=True, default=shortuuid.uuid, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    name = models.CharField(max_length=255, blank=False, unique=True)
    user = models.ForeignKey(User, null=True)  # should not be NULL from now on

    class Meta:
        unique_together = ('name', 'user')

    def assign_all_recipes(self):
        for recipe in recipe_controller.recipes:
            self.recipe_set.create(name=recipe)

    def init_recipes(self):
        """
        Start a thread to initialize all recipes.
        :return:
        If all recipes were already initialized, return True.
        """


class Recipe(models.Model):
    INIT_FAILED = 'FA'
    INIT_NONE = 'NO'
    INIT_PROGRESS = 'PR'
    INIT_SUCCESS = 'SU'

    INIT_STATUS_CHOICES = (
        (INIT_NONE, 'Not initialized'),
        (INIT_FAILED, 'Initialization failed'),
        (INIT_PROGRESS, 'Initializing'),
        (INIT_SUCCESS, 'Initialized'),
    )

    id = models.CharField(max_length=255, primary_key=True, default=shortuuid.uuid, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    name = models.CharField(max_length=255, editable=False)
    json_string = models.TextField(default='')
    app = models.ForeignKey(App, null=True)  # should not be NULL from now on
    init_status = models.CharField(max_length=2, choices=INIT_STATUS_CHOICES, default=INIT_NONE)

    def __str__(self):
        tag = self.name.title() + ' Recipe'
        owner = '{}:{}'.format(self.app.user.email, self.app.name)
        init = self.get_init_status_display()
        return '{:10} [{:30}] [{:20}]'.format(tag, owner, init)

    def get_api(self, credentials):
        api_cls = core.api.api_dict[self.name]
        return api_cls(credentials, self.app.id, self.json_string)

    def save_recipe(self, api: core.api.API):
        self.json_string = api.get_recipe_controller().to_json()
        self.save()

    @contextmanager
    def api(self, credentials):
        """
        You can do this:
            with recipe.api() as api:
                use(api)
        Instead of this:
            api = recipe.api()
            use(api)
            recipe.save_recipe(api)
        :param credentials:
        :return:
        """
        api = self.get_api(credentials)
        yield api
        self.save_recipe(api)


    def init(self, credentials):
        api = self.get_api(credentials)
        api.apply()  # wtf? >> ask developers plz. no time to explain
