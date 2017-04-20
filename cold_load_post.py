import os

import django
import better_exceptions
from better_exceptions import color
from django.db import transaction
from django.db.models import Q

from progressbar import Progress

better_exceptions.MAX_LENGTH = None

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dyplom.settings")


django.setup()
from vkontakte.models import *
print("Run")
api = VkConnector.default().api

i = 0
students = VkUser.objects.filter(Q(my_nsu_user__isnull=False) | Q(university=671))
print("Found {} stundents".format(len(students)))

p_all_before = VkPost.objects.count()
p_count = 0

progress = Progress(max_value=students.count())

for student in students:
    with transaction.atomic():
        from_time = student.last_post_time
        posts = api.get_wall_posts(user=student, from_time=from_time)
        for p in posts:
            p_count += 1

    progress.update()
    progress.user_str = "+{} posts, {} all".format(
        p_count,
        p_all_before + p_count
    )
