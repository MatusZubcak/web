# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.conf import settings
import os
from uuidfield import UUIDField
from django.contrib.auth.models import Group
from datetime import datetime
import pytz


@python_2_unicode_compatible
class Repository(models.Model):
    notification_string = UUIDField(
        auto=True, primary_key=True, version=4, verbose_name='string pre push notifikáciu'
    )
    url = models.CharField(max_length=128, verbose_name='url git repozitára')

    class Meta:
        verbose_name = 'Repozitár'
        verbose_name_plural = 'Repozitáre'

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Competition(models.Model):
    '''
    Consists of series.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    sites = models.ManyToManyField(Site)
    repo = models.ForeignKey(Repository, null=True, blank=True, verbose_name='git repozitár')
    repo_root = models.CharField(
        max_length=128, verbose_name='adresa foldra súťaže v repozitári'
    )
    organizers_group = models.ForeignKey(Group, null=True, verbose_name='skupina vedúcich')

    class Meta:
        verbose_name = 'Súťaž'
        verbose_name_plural = 'Súťaže'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Series(models.Model):
    '''
    Series consists of several rounds.
    '''
    competition = models.ForeignKey(Competition, verbose_name='súťaž')
    name = models.CharField(max_length=32, verbose_name='názov')
    number = models.IntegerField(verbose_name='číslo série')
    year = models.IntegerField(verbose_name='ročník')

    class Meta:
        verbose_name = 'Séria'
        verbose_name_plural = 'Série'

    def __str__(self):
        return '%i. (%s) séria, %i. ročník %s'\
            % (self.number, self.name, self.year, self.competition)

    def short_str(self):
        return '%i. (%s) séria'\
            % (self.number, self.name)
    short_str.short_description = 'Séria'


@python_2_unicode_compatible
class Round(models.Model):
    '''
    Round has tasks.
    Holds information about deadline and such things
    '''
    series = models.ForeignKey(Series, verbose_name='séria')
    number = models.IntegerField(verbose_name='číslo')
    start_time = models.DateTimeField(verbose_name='začiatok')
    end_time = models.DateTimeField(verbose_name='koniec')
    visible = models.BooleanField(verbose_name='viditeľnosť')
    solutions_visible = models.BooleanField(verbose_name='viditeľnosť vzorákov')

    @property
    def can_submit(self):
        if datetime.now(pytz.utc) <= self.end_time:
            return True
        return False

    def get_base_path(self):
        round_dir = '{}{}'.format(self.number, settings.TASK_STATEMENTS_SUFFIX_ROUND)
        year_dir = '{}{}'.format(self.series.year, settings.TASK_STATEMENTS_SUFFIX_YEAR)
        competition_name = self.series.competition.name
        path = os.path.join(
            settings.TASK_STATEMENTS_PATH,
            competition_name,
            year_dir,
            round_dir,
        )
        if not os.path.exists(path):
            raise IOError("path '%s' doesn't exist" % path)
        return path

    def get_path(self, solution=False):
        path_type = settings.TASK_STATEMENTS_SOLUTIONS_DIR if solution\
            else settings.TASK_STATEMENTS_TASKS_DIR
        path = os.path.join(
            self.get_base_path(),
            path_type,
        )
        if not os.path.exists(path):
            raise IOError("path '%s' doesn't exist" % path)
        return path

    def get_pdf_path(self, solution=False):
        pdf_file = settings.TASK_STATEMENTS_SOLUTIONS_PDF if solution\
            else settings.TASK_STATEMENTS_PDF
        path = os.path.join(
            self.get_path(solution),
            pdf_file,
        )
        if not os.path.exists(path):
            raise IOError("path '%s' doesn't exist" % path)
        return path

    def get_pictures_path(self):
        path = os.path.join(
            self.get_base_path(),
            settings.TASK_STATEMENTS_PICTURES_DIR,
        )
        if not os.path.exists(path):
            raise IOError("path '%s' doesn't exist" % path)
        return path

    @property
    def tasks_pdf_exists(self):
        try:
            self.get_pdf_path(solution=False)
            return True
        except IOError:
            return False

    @property
    def solutions_pdf_exists(self):
        try:
            self.get_pdf_path(solution=True)
            return True
        except IOError:
            return False

    @staticmethod
    def visible_rounds(user):
        if user.is_superuser:
            return Round.objects
        else:
            return Round.objects.filter(
                Q(series__competition__organizers_group__in=user.groups.all())
                | Q(visible=True)
            )

    @staticmethod
    def get_latest_by_competition(user):
        rounds = Round.visible_rounds(user).order_by(
            'series__competition', '-end_time'
        ).distinct(
            'series__competition'
        ).select_related(
            'series__competition'
        )
        return {r.series.competition: r for r in rounds}

    def visible_for_user(self, user):
        return user.is_superuser\
            or self.series.competition.organizers_group in user.groups.all()\
            or self.visible

    def solutions_visible_for_user(self, user):
        return user.is_superuser\
            or self.series.competition.organizers_group in user.groups.all()\
            or self.solutions_visible

    class Meta:
        verbose_name = 'Kolo'
        verbose_name_plural = 'Kolá'

    def __str__(self):
        return '%i. kolo, %i. séria, %i. ročník %s'\
            % (self.number, self.series.number, self.series.year, self.series.competition)

    def short_str(self):
        return '%i. kolo' % self.number
    short_str.short_description = 'kolo'
