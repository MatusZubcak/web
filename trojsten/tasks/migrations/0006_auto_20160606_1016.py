# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 08:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20160506_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='tester_response',
            field=models.CharField(blank=True, help_text='O\u010dak\xe1van\xe9 odpovede s\xfa OK, EXC, WA, SEC, TLE, IGN, CERR', max_length=10, verbose_name='odpove\u010f testova\u010da'),
        ),
    ]