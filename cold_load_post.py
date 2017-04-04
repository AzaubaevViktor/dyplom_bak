import django
django.setup()
from vkontakte.models import *
print("Run")
connector = VkConnector.objects.get(id=1)

i = 0
u = VkUser.objects.get(id=1)
for p in connector.api.get_wall_posts(users=[u], count=2500):
    i += 1
    print(p, i)
