from django.contrib import admin

from my_nsu.models import MyNsuUser


@admin.register(MyNsuUser)
class MyNsuUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'first_name',
                    'last_name',
                    'group',
                    'faculty',
                    'user_type',
                    'qualification')
    search_fields = ('first_name', 'last_name')