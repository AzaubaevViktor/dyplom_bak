from django.db import models

# Create your models here.
from vkontakte.models import VkPost


class Lemma(models.Model):
    name = models.CharField(max_length=100, unique=True)

    @property
    def meets_count(self):
        return self.meets.count()

    def __str__(self):
        return self.name


class LemmaMeet(models.Model):
    lemma = models.ForeignKey(
        Lemma,
        on_delete=models.CASCADE,
        related_name='meets')
    timestamp = models.IntegerField()
    post = models.ForeignKey(
        VkPost,
        on_delete=models.CASCADE,
        related_name='lemma_meets')

    @property
    def post_text(self):
        return self.post.text
