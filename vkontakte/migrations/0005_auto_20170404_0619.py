# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 06:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vkontakte', '0004_auto_20170404_0609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkpost',
            name='_date',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='vkpost',
            name='date',
            field=models.DateField(null=True),
        ),
    ]