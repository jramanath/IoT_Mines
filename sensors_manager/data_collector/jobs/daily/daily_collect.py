# -*- coding: utf-8 -*-
"""
Job régulier permettant de lancer
la récupération des données sur Amazon S3
"""

from django_extensions.management.jobs import DailyJob


class Job(DailyJob):
    help = u"Job récupérant les données sur S3"

    def execute(self):
        from django.core import management

        # on lance le script de récupération
        management.call_command('collect_S3')
