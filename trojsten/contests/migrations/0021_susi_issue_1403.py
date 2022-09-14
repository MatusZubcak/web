# Generated by Django 2.2.24 on 2022-08-09 15:48
# Modified by milos7250 on 2022-08-09 16:15

from datetime import timedelta

from django.db import migrations, models

from trojsten.rules.susi_constants import SUSI_COMPETITION_ID

# Susi's constants at the time of creating this migration. Not importing the constants from
# trojsten.rules.susi_constants as they will get deleted soon.
SUSI_DISCOVERY_ROUND_NUMBER = 100
SUSI_BIG_HINT_DAYS = 4


def set_big_hint_time_for_old_rounds(apps, schema_editor):
    Round = apps.get_model("contests", "Round")
    for round_ in Round.objects.filter(semester__competition=SUSI_COMPETITION_ID):
        if round_.susi_big_hint_time is None:
            round_.susi_big_hint_time = round_.end_time + timedelta(days=SUSI_BIG_HINT_DAYS)
            round_.save()


def set_discovery_status_for_old_rounds(apps, schema_editor):
    Round = apps.get_model("contests", "Round")
    for round_ in Round.objects.filter(semester__competition=SUSI_COMPETITION_ID):
        if round_.number == SUSI_DISCOVERY_ROUND_NUMBER:
            round_.susi_is_discovery = True
            round_.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("contests", "0020_auto_20200923_0906"),
    ]

    operations = [
        migrations.AddField(
            model_name="round",
            name="susi_big_hint_time",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="zverejnenie veľkého hintu"
            ),
        ),
        migrations.RunPython(code=set_big_hint_time_for_old_rounds, reverse_code=do_nothing),
        migrations.AddField(
            model_name="round",
            name="susi_is_discovery",
            field=models.BooleanField(default=False, verbose_name="Objavné kolo"),
        ),
        migrations.RunPython(code=set_discovery_status_for_old_rounds, reverse_code=do_nothing),
    ]
