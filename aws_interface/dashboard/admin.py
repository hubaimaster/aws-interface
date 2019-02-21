from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, App, Recipe

admin.site.register(User, UserAdmin)
admin.site.register(App)
admin.site.register(Recipe)
