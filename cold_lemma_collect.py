import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dyplom.settings")
django.setup()

from django.db import transaction

from progressbar import Progress
from mystem_utils import handle_posts

import better_exceptions

better_exceptions.MAX_LENGTH = None

import pymystem3
from django.db.models import Q

from lemmatize.models import Lemma, LemmaMeet
from vkontakte.models import VkPost, VkConnector

print("Run")
api = VkConnector.default().api

if 'y' == input("Drop lemmas? [y/N]"):
    Lemma.objects.all().delete()
    print("All lemmas deleted")

print("Get all posts")
query = VkPost.objects.filter(~Q(text=""))
posts_count = query.count()

print("Init Mystem")
mystem = pymystem3.Mystem()

transaction_len = 1000
progress = Progress(max_value=posts_count, item_name="p", significant=transaction_len)

lemmas_count = 0

try:
    lp = iter(handle_posts(query))

    prev_post = None

    while True:
        with transaction.atomic():
            data = next(lp)
            if data:
                lemma, post = data
                if isinstance(lemma, str):
                    if "new_post" == lemma:
                        prev_post = post
                        progress.user_str = "LemmaMeets: {}".format(
                            lemmas_count)
                        progress.update()
                else:
                    lmm = LemmaMeet.objects.create(
                        lemma=lemma,
                        timestamp=post.timestamp,
                        post=post
                    )
                    lemmas_count += 1

            if 0 == lemmas_count % transaction_len:
                # for transaction
                continue

except StopIteration:
    pass





