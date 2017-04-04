import django


django.setup()
from vkontakte.models import *
from vkontakte.utils import print_line

print("Run")
api = VkConnector.default().api

groups = VkGroup.objects.all()

print(groups)

count = 0
for group in groups:
    print(group.name)
    for users in api.get_group_users(group):
        count += 1
        print_line('Load {} users'.format(count))
