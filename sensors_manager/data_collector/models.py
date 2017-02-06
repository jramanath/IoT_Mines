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

    id = models.AutoField(primary_key=True)
    file = models.CharField(max_length=100, blank=True, null=True)

    objects = DataFrameManager()

    class Meta(object):
        managed = True
        db_table = 'data_loader'


#  Créer le modèle des autres tables