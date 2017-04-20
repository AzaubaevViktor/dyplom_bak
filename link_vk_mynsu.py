from datetime import date

import django
from django.db import transaction

django.setup()

from transliterate import translit

from my_nsu.models import MyNsuUser
from vkontakte.models import VkUser
from progressbar import Progress


def ru_to_en(s: str) -> str:
    return translit(s, language_code='ru', reversed=True)

print("Get students from my.nsu.ru ...")
students = MyNsuUser.objects.filter(user_type='student')

print("Students: {}/{}".format(
    students.count(),
    MyNsuUser.objects.count()
))

progress = Progress(max_value=students.count())

with transaction.atomic():
    for student in students:
        # try find by name and last name with translit
        query_set = VkUser.objects.filter(
            first_name=student.first_name,
            last_name=student.last_name
        ).union(
            VkUser.objects.filter(
                first_name=ru_to_en(student.first_name),
                last_name=ru_to_en(student.last_name)
            )
        )

        if len(query_set) == 1:
            student.vk_user = query_set[0]
            student.save()
        elif len(query_set) > 1:
            # Получаем из группы примерный возраст
            birth_year = 2000 + int(student.group[:2]) - 18
            dt = date(year=birth_year, month=9, day=1)

            deltas = []
            # Сортируем по дельте вычисленной даты рождения и реальной
            for user in query_set:
                if user.bdate:
                    td = dt - user.bdate
                    if td.days > 3 * 365:
                        continue
                    deltas.append((abs(td), user))

            deltas.sort(key=lambda i: i[0])

            if len(deltas) > 0:
                student.vk_user = deltas[0][1]
                student.save()

        progress.update()
