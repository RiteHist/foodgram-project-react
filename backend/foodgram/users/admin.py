from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',
                    'first_name', 'last_name')
    list_filter = ('username',)


admin.site.register(models.User, UserAdmin)
