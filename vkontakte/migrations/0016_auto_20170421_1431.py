# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-21 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vkontakte', '0015_auto_20170419_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkpost',
            name='owner_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='vkontakte.VkUser'),
        ),
    ]
