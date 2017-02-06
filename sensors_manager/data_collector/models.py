# -*- coding: utf-8 -*-
"""
Modèle des données du projet
"""
from __future__ import unicode_literals

from django.db import models
from django_pandas.managers import DataFrameManager


class DataLoader(models.Model):
    """
    Table contenant le nom des fichiers déjà collectés
    """

    id = models.AutoField(primary_key=True)  # id unique
    file = models.CharField(max_length=100, blank=True, null=True)  # nom du json
    status = models.NullBooleanField(blank=True, null=True)  # statut de l'import

    objects = DataFrameManager()

    class Meta(object):
        managed = True
        db_table = 'data_loader'


class DataTISensor(models.Model):
    """
    Table contenant les données des capteurs Texas Instrument
    """

    id = models.AutoField(primary_key=True)  # id unique
    creation = models.DateTimeField(auto_now=False, auto_now_add=False)  # date et heure
    temperature = models.FloatField(null=True, blank=True)  # température en degrés celsius
    humidity = models.FloatField(null=True, blank=True)  # humidité en pourcentage
    illuminance = models.FloatField(null=True, blank=True)  # luminosité
    sensor = models.CharField(max_length=100, blank=True, null=True)  # sensor id

    objects = DataFrameManager()

    class Meta(object):
        managed = True
        db_table = 'data_ti'


class DataWindowsSensor(models.Model):
    """
    Table contenant les données des capteurs
    d'ouverture des fenêtres
    """

    id = models.AutoField(primary_key=True)  # id unique
    creation = models.DateTimeField(auto_now=False, auto_now_add=False)  # date et heure
    sensor = models.CharField(max_length=100, blank=True, null=True)  # sensor id
    windows_state = models.NullBooleanField(blank=True, null=True)  # état d'ouverture de la fenetre

    objects = DataFrameManager()

    class Meta(object):
        managed = True
        db_table = 'data_window'
