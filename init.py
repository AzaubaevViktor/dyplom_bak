from pprint import pprint

import django
django.setup()
from vkontakte.models import *

api = VkConnector.default().api

groups = api.get_groups(['typical_nsu', 'nsu24'])
for group in groups:
    pprint(group)
