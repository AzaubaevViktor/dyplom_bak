import django

from vkontakte.utils import print_line

django.setup()
from vkontakte.models import *
print("Run")
api = VkConnector.default().api

c = input("Do you really want to delete all VK Groups, Users and Posts? [y/N]")

if 'y' == c:
    VkGroup.objects.all().delete()
    print("Groups deleted")
    VkUser.objects.all().delete()
    print("Users deleted")
    VkPost.objects.all().delete()
    print("Posts deleted")
