import django

from vkontakte.utils import print_line

django.setup()
from vkontakte.models import *
print("Run")
api = VkConnector.default().api

c = input("Do you really want to delete all DB? [y/N]")

if 'y' == c:

    VkGroup.objects.all().delete()
    VkUser.objects.all().delete()
    VkPost.objects.all().delete()
