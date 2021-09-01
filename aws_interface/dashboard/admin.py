from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import Upper
from .models import User, App, Log, MarketplaceLogic, MarketplaceLogicComment, MarketplaceLogicSetup, OTPCode


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'creation_date')
    ordering = ['-creation_date']


class AppAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'creation_date']
    fields = ['id', 'creation_date', 'name', 'user', 'vendor']
    list_display = ('id', 'creation_date', 'name', 'user', 'vendor')
    ordering = ['-creation_date']

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


class OTPCodeAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'email']
    list_display = ('id', 'email')


admin.site.register(User, CustomUserAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(OTPCode, OTPCodeAdmin)

admin.site.register(MarketplaceLogic, MarketplaceLogicAdmin)
admin.site.register(MarketplaceLogicComment)
admin.site.register(MarketplaceLogicSetup)
