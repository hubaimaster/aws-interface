from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import Upper, Lower
from .models import User, App, Log


class CustomUserAdmin(UserAdmin):
    fields = ['c_credentials']

    def get_ordering(self, request):
        return [Upper('creation_date')]


class AppAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'creation_date']
    fields = ['id', 'creation_date', 'name', 'user', 'vendor']
    list_display = ('id', 'creation_date', 'name', 'user', 'vendor')

    def get_ordering(self, request):
        return [Upper('creation_date')]


class LogAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'creation_date', 'user', 'level', 'event']
    list_display = ('level', 'creation_date', 'user', 'event')
    ordering = ['-creation_date']
    search_fields = ['level', 'event']
    list_filter = ['level', 'user']


admin.site.register(User, UserAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Log, LogAdmin)
