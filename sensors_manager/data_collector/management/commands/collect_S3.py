# -*- coding: utf-8 -*-
"""
Script permettant de récupérer des données
sur S3

Script actionné par un cron qui tourne toutes les 5 mn
"""

from datetime import datetime, timedelta
import pytz
import logging
import data_collector.utils as dtutils
import pandas as pd
import numpy as np

from django.core.management.base import BaseCommand
from constance import config
from django.utils.encoding import force_bytes


class Command(BaseCommand):

    help = 'S3 data collector'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        now = pytz.utc.localize(datetime.now())
        pretty_now = dtutils.datetime_format(now)
        msg = (u'Script collect_S3 '
               u'commencé le {}'.format(pretty_now))
        self.stdout.write(msg)
        self.stdout.flush()
        logger.info(msg)

        # créer la connexion à S3

        # identifier les fichiers à ajouter à la base de données

        # parser les nouveaux fichiers

        # les ajouter à la base de donnée
        # mettre à jour aussi DataLoader

        # fin = arrêt de la connexion S3

        logger.info(u'Les données ont été ajoutées à la BDD')

        now = pytz.utc.localize(datetime.now())
        pretty_now = dtutils.datetime_format(now)
        msg = u'Script collect_S3, terminé le {}'.format(pretty_now)
        self.stdout.write(msg)
        logger.info(msg)