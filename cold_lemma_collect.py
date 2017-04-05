import django
import time

from django.db import transaction

django.setup()
import better_exceptions
from better_exceptions import color

import pymystem3
from django.db.models import Q

from lemmatize.models import Lemma, LemmaMeet
from vkontakte.models import VkPost, VkConnector

better_exceptions.MAX_LENGTH = None

from vkontakte.utils import print_line


def lemmas_filter(lms):
    for lemma in lms:
        if '\1' in lemma:
            yield '\1'
        if lemma.isalpha() and len(lemma) <= 100:
            lemma_db, _ = Lemma.objects.get_or_create(name=lemma.strip())
            lemma_db.save()
            yield lemma_db


def remain(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


print("Run")
api = VkConnector.default().api

if 'y' == input("Drop lemmas? [y/N]"):
    Lemma.objects.all().delete()
    print("All lemmas deleted")

posts = VkPost.objects.filter(~Q(text="")).all()
len_posts = len(posts)
print("Fount {} posts with text".format(len_posts))

print("Init Mystem")
mystem = pymystem3.Mystem()

post_count = 0
lemmas_count = 0


st = time.time()

pi = posts.iterator()


def posts_handle(posts):
    _lemmas_count = 0
    text = ""
    for post in posts:
        text += post.text + " \1 "  # break symbol

    lemmas = lemmas_filter(mystem.lemmatize(text))

    post_i = 0
    for lemma in lemmas:
        if '\1' == lemma:
            post_i += 1
        else:
            lmm = LemmaMeet(lemma=lemma,
                            timestamp=post.timestamp,
                            post=posts[post_i])
            lmm.save()
            _lemmas_count += 1

    return _lemmas_count

end_cycle = False
while not end_cycle:
    with transaction.atomic():
        posts = []
        for i in range(100):
            try:
                posts.append(next(pi))
            except StopIteration:
                end_cycle = True
                break

        lemmas_count += posts_handle(posts)

        post_count += 100

    t = time.time() - st
    speed = post_count / t
    print_line(
        "{} lemmas from {} posts ({:.2f}sec, {:.2f}posts/sec, "
        "remain {})".format(
        lemmas_count,
        post_count,
        t,
        speed,
        remain((len_posts - post_count) / speed)
    ))

