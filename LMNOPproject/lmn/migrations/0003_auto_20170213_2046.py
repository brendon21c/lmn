# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-02-13 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0002_auto_20170211_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
