# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-22 15:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl', '0007_auto_20191116_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='news_source',
            field=models.CharField(choices=[('DN', 'THE DAILY NATION'), ('BD', 'THE BUSINESS DAILY'), ('EA', 'THE EAST AFRICAN'), ('CT', 'THE CITIZEN'), ('SM', 'THE DAILY STANDARD')], max_length=100),
        ),
    ]
