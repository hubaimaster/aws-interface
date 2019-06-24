from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import Upper
from .models import User, App, Log, MarketplaceLogic, MarketplaceLogicComment


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


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'tracker', 'creation_date', 'user', 'action', 'target']
    list_display = ('id', 'tracker', 'creation_date', 'user', 'action', 'target')
    ordering = ['creation_date']
    search_fields = ['id', 'tracker', 'creation_date', 'user', 'action', 'target']
    list_filter = ['user', 'tracker', 'action', 'target']


class MarketplaceLogicAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'creation_date']
    list_display = ('id', 'title', 'creation_date', 'user', 'description')
    ordering = ['creation_date']


admin.site.register(User, UserAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Log, LogAdmin)

admin.site.register(MarketplaceLogic, MarketplaceLogicAdmin)
admin.site.register(MarketplaceLogicComment)
