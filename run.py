import django
django.setup()
from vkontakte.models import *
print("Run")
connector = VkConnector.objects.get(id=1)

print(list(connector.api.get_users([0, 1, 2, 3])))
