# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vkontakte', '0008_auto_20170404_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkpost',
            name='post_id',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
    ]