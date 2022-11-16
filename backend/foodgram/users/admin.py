from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy
from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',
                    'first_name', 'last_name')
    list_filter = ('username',
                   'email')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Follow, FollowAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
