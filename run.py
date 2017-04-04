import django
django.setup()
from vkontakte.models import *
print("Run")
connector = VkConnector.objects.get(id=1)

i = 0
for u in connector.api.get_users(range(10000)):
    i += 1
    print(u, i)
