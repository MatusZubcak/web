# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-09-15 20:02
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("old_submit", "0004_submit_protocol")]

    operations = [
        migrations.AlterField(
            model_name="submit",
            name="protocol_id",
            field=models.CharField(
                blank=True, db_index=True, max_length=128, verbose_name="číslo protokolu"
            ),
        ),
        migrations.AlterField(
            model_name="submit",
            name="submit_type",
            field=models.IntegerField(
                choices=[(0, "source"), (1, "description"), (2, "testable_zip"), (3, "external")],
                verbose_name="typ submitu",
            ),
        ),
        migrations.AlterField(
            model_name="submit",
            name="tester_response",
            field=models.CharField(
                blank=True,
                help_text="Očakávané odpovede sú WA, CERR, TLE, MLE, OK, EXC, SEC, IGN, PROTCOR",
                max_length=10,
                verbose_name="odpoveď testovača",
            ),
        ),
        migrations.AlterField(
            model_name="submit",
            name="testing_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("reviewed", "reviewed"),
                    ("in queue", "in queue"),
                    ("finished", "finished"),
                    ("OK", "OK"),
                ],
                max_length=128,
                verbose_name="stav testovania",
            ),
        ),
    ]
