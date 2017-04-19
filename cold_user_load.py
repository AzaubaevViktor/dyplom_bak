import django
django.setup()

from progressbar import Progress

import better_exceptions
better_exceptions.MAX_LENGTH = None
from better_exceptions import color

from vkontakte.models import *

print("Cold User Load")
api = VkConnector.default().api
print("VkApi ok")

groups = VkGroup.objects.all()

print("Groups: {}".format(groups))


for group in groups:
    print("Load from {}".format(group.name))

    progress = Progress(max_value=1, item_name="u")
    for user, count in api.get_group_users(group):
        progress.update_max(count)
        progress.update()

