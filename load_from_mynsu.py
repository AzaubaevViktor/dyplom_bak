import django
django.setup()

from my_nsu.models import MyNsuUser
from progressbar import Progress

import better_exceptions
from better_exceptions import color

better_exceptions.MAX_LENGTH = None

print("Load users from http://my.nsu.ru/")

print("Find from 90000")

progress = Progress(max_value=90000, item_name='u')

i = 63880
progress.current_value = 63880
errors = 0
while i < progress.max_value:
    user = MyNsuUser.objects.get_from_site(i)
    if user is None:
        errors += 1
    else:
        errors = 0

    if i == progress.max_value - 1:
        if errors > 200:
            break
        else:
            progress.update_max(progress.max_value + 200)

    progress.update()
    i += 1