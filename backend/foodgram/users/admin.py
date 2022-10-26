from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',
                    'first_name', 'last_name')
    list_filter = ('username',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Follow, FollowAdmin)
