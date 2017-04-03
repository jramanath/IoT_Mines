# -*- coding: utf-8 -*-
"""
Script permettant de récupérer les données de capteur
sur un bucket S3 ou en local

Script actionné par un cron qui tourne toutes les 5 mn
"""

from datetime import datetime
import pytz
import logging
import boto
import boto.s3.connection
import json
import pandas as pd
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from data_collector.models import DataLoader, DataTISensor, DataWindowsSensor
from constance import config


def datetime_format(dt):
    paris_tz = pytz.timezone('Europe/Paris')
    paris_dt = dt.astimezone(paris_tz)
    template = (u"{dt.day:02d}/{dt.month:02d}/{dt.year:04d} "
                u"à {dt.hour}h{dt.minute:02d}")
    return template.format(dt=paris_dt)


class BadS3FilesException(IOError):
    """
    Classe indiquant une erreur dans la lecture
    d'un fichier du bucket S3
    """


class BadParametersException(ValueError):
    """
    Classe indiquant un paramètre manquant
    dans un fichier json de capteurs
    """


class S3Connection(object):
    """
    Une classe générique permettant de se connecter
    à un bucket S3 et de récupérer tous les fichiers json présents
    """

    def __init__(self, bucket_name=None, **kwargs):
        # connecteur
        conn = boto.s3.connect_to_region(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.REGION_NAME,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
            **kwargs
        )
        self.conn = conn

        # bucket
        self.mybucket = None
        self.files = []

        if bucket_name is not None:
            mybucket = conn.get_bucket(bucket_name, validate=False)
            self.mybucket = mybucket

            # fichiers json du bucket
            files = mybucket.list()
            files = [f for f in files if '.json' in f.key]
            self.files = files


class ParsingTIFiles(object):
    """
    Classe responsable du parsing
    des json venant des capteurs TI
    """

    def __init__(self, data):
        logger = logging.getLogger(__name__)
        try:
            data = json.load(data)

        except Exception as e:
            msg = u"Erreur dans la lecture du fichier: {e.args[0]}"
            logger.error(msg.format(e=e))
            raise ValueError(msg)

        try:
            self.creation = data['creation_datetime']
            self.temperature = data['Temperature']
            self.humidity = data['Humidite']
            self.illuminance = data['Luminosite']
            self.sensor = data['ID']

        except KeyError as e:
            msg = u"Paramètre manquant: {e.args[0]}"
            logger.error(msg.format(e=e))
            raise BadParametersException(msg)

        self.measure = [self.creation, self.temperature, self.humidity, self.illuminance,
                        self.sensor]


class ParsingWindowsFiles(object):
    """
    Classe responsable du parsing
    des json venant des capteurs de fenêtre
    """

    def __init__(self, data):
        logger = logging.getLogger(__name__)
        try:
            data = json.load(data)

        except Exception as e:
            msg = u"Erreur dans la lecture du fichier: {e.args[0]}"
            logger.error(msg.format(e=e))
            raise ValueError(msg.format(e=e))

        # conversion json

        try:
            self.creation = data['creation_datetime']
            self.tableau = data['Tableau']
            self.milieu = data['Milieu']
            self.fond = data['Fond']

        except KeyError as e:
            msg = u"Paramètre manquant: {e.args[0]}"
            logger.error(msg.format(e=e))
            raise BadParametersException(msg.format(e=e))

        self.measure = [self.creation, self.tableau, self.milieu, self.fond]


def loading_manager():
    """
    Cette fonction gère la récupération
    des données du bucket S3
    """
    logger = logging.getLogger(__name__)

    # fichiers déjà passés en revue
    qs = DataLoader.objects.values('id', 'file')

    files_in_bdd = pd.DataFrame.from_records(qs)
    if len(files_in_bdd):
        files_in_bdd = files_in_bdd['file'].values.tolist()
    else:
        files_in_bdd = []

    # fichiers à ajouter à la base de données

    if settings.S3_OPTION:
        # connexion à S3
        s3_connector = S3Connection(bucket_name=settings.BUCKET_NAME)
        files_to_load = [(f, str(f.key)) for f in s3_connector.files if
                         str(f.key) not in files_in_bdd]
    else:
        files_to_load = [(f, f) for f in os.listdir(settings.CACHE_DIR) if
                         f not in files_in_bdd]

    logger.info(u"Nb de nvx fichiers de mesures "
                u"passés en revue : %s ", len(files_to_load))

    # parser les nouveaux fichiers
    # et concaténer les mesures à ajouter à la bdd
    TI_measures = []
    windows_measures = []
    loaded_files = []

    for f, name in files_to_load:
        # une mesure de TI
        if 'TI' in name:
            try:
                if settings.S3_OPTION:
                    data = f.get_contents_as_string()
                    parsed_file = ParsingTIFiles(data)
                else:
                    filepath = settings.CACHE_DIR + name
                    with open(filepath) as data:
                        parsed_file = ParsingTIFiles(data)

                TI_measures.append(parsed_file.measure)
                loaded_files.append([name, True])

            except Exception as e:
                msg = u"Erreur de parsing : {e.args[0]}"
                logger.error(msg.format(e=e))

        elif 'windows' in name:
            try:
                if settings.S3_OPTION:
                    data = f.get_contents_as_string()
                    parsed_file = ParsingTIFiles(data)
                else:
                    filepath = settings.CACHE_DIR + name
                    with open(filepath) as data:
                        parsed_file = ParsingTIFiles(data)

                windows_measures.append(parsed_file.measure)
                loaded_files.append([name, True])
            except Exception as e:
                msg = u"Erreur de parsing : {e.args[0]}"
                logger.error(msg.format(e=e))

        else:
            loaded_files.append([name, False])

    # on insère en bulk

    # mesures de fenêtre

    _cols = ['creation', 'tableau', 'milieu', 'fond']
    windows_measures = pd.DataFrame(windows_measures, columns=_cols)
    logger.info(u"Nb de mesures fenêtre ajoutées : %s ", len(windows_measures))

    if len(windows_measures):
        new_objects = [DataWindowsSensor(creation=row['creation'],
                                         tableau=row['tableau'],
                                         milieu=row['milieu'],
                                         fond=row['fond'])
                       for index, row in windows_measures.iterrows()]

        DataWindowsSensor.objects.bulk_create(new_objects)

    # mesures de TI

    # Faut il changer ici aussi les noms des paramètres des cpateurs TI ?

    _cols = ['creation', 'temperature', 'humidity', 'illuminance', 'sensor']
    TI_measures = pd.DataFrame(TI_measures, columns=_cols)
    logger.info(u"Nb de mesures TI ajoutées : %s ", len(TI_measures))

    if len(TI_measures):
        new_objects = [DataTISensor(creation=row['creation'],
                                    temperature=row['temperature'],
                                    humidity=row['humidity'],
                                    illuminance=row['illuminance'],
                                    sensor=row['sensor'])
                       for index, row in TI_measures.iterrows()]

        DataTISensor.objects.bulk_create(new_objects)

    # fichiers chargés
    _cols = ['file', 'status']
    loaded_files = pd.DataFrame(loaded_files, columns=_cols)

    if len(loaded_files):
        new_objects = [DataLoader(file=row['file'],
                                  status=row['status'])
                       for index, row in loaded_files.iterrows()]

        DataLoader.objects.bulk_create(new_objects)

    # fin = arrêt de la connexion S3
    if settings.S3_OPTION:
        s3_connector.conn.close()


class Command(BaseCommand):

    help = 'S3 data collector'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        now = pytz.utc.localize(datetime.now())
        pretty_now = datetime_format(now)
        msg = (u'Script collect_S3 '
               u'commencé le {}'.format(pretty_now))
        self.stdout.write(msg)
        self.stdout.flush()
        logger.info(msg)

        # vérification script en cours
        if config.S3_COLLECT_IN_PROGRESS:
            logger.error(u"Attention, script collect_S3 "
                         u"déjà en cours d'exécution, opération "
                         u"annulée")
            return

        config.S3_COLLECT_IN_PROGRESS = True

        # exécution en fonction du mode de mise à jour
        try:
            loading_manager()
            logger.info(u'Les données ont été ajoutées à la BDD')
        except Exception as e:
            logger.error(repr(e), exc_info=True)
            raise
        finally:
            # script terminé
            config.S3_COLLECT_IN_PROGRESS = False

        now = pytz.utc.localize(datetime.now())
        pretty_now = datetime_format(now)
        msg = u'Script collect_S3, terminé le {}'.format(pretty_now)
        self.stdout.write(msg)
        logger.info(msg)
