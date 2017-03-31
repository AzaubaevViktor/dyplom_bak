from django.contrib import admin

# Register your models here.
from vkontakte.models import *


@admin.register(VkConnector)
class VkConnectorAdmin(admin.ModelAdmin):
    fields = ('app_id', '_token')


@admin.register(VkUser)
class VkUserAdmin(admin.ModelAdmin):
    fields = (
        'row',
        'sex',
        'first_name',
        'last_name',
        '_bdate',
        'bdate',
        'university',
        'graduation',
        'twitter',
    )


@admin.register(VkGroup)
class VkGroupAdmin(admin.ModelAdmin):
    fields = ('users', )


@admin.register(VkPost)
class VkPostAdmin(admin.ModelAdmin):
    fields = (
        'row',
        '_date',
        'date',
        'owner_user',
        'owner_group',
        'text',
        'reposts',
        'likes',
        'source'
    )