import django
import better_exceptions
from better_exceptions import color

better_exceptions.MAX_LENGTH = None

from vkontakte.utils import print_line

django.setup()
from vkontakte.models import *
print("Run")
api = VkConnector.default().api

i = 0
students = VkUser.objects.filter(university=671).all()
print("Found {} stundents".format(len(students)))

s_count = 0
p_count = 0

for student in students:
    s_count += 1
    posts = api.get_wall_posts(users=[student], count=1000)
    for p in posts:
        p_count += 1

    print_line("{} posts from {} students".format(
        p_count,
        s_count
    ))
