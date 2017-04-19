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
        'day',
        'month',
        'year'
        'university',
        'graduation',
    )

    list_display = ('id', 'vk_link', 'first_name', 'last_name',
                    'university', 'faculty', 'date_str', 'graduation',)
    search_fields = ('university', 'last_name', 'first_name')


@admin.register(VkGroup)
class VkGroupAdmin(admin.ModelAdmin):
    fields = ('row', 'name', 'users', )
    list_display = (
        'id', 'name', 'users_count'
    )


@admin.register(VkPost)
class VkPostAdmin(admin.ModelAdmin):
    fields = (
        'post_id',
        'row',
        '_date',
        'date',
        'owner_user',
        'owner_group',
        'text',
        'reposts',
        'likes',
        'source_data'
    )

    list_display = ('id', 'vk_link', 'post_id', 'owner_user', 'text', 'reposts', 'likes')
