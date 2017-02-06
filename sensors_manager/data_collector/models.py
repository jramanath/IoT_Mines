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

    # à mettre pour chaque table
    id = models.AutoField(primary_key=True)
    # on va y mettre l'identification du fichier json
    file = models.CharField(max_length=100, blank=True, null=True)

    #va permettre l'analyse de données
    objects = DataFrameManager()

    # convertit classe meta en data_frame (passer de queryset à column=[id, file])
    #remplace DataLoader.objects.all().to.data_frame()
    class Meta(object):
        managed = True
        db_table = 'data_loader'

class DataCapteursTI(models.Model):
    """
    Table contenant les données des capteurs
    """

    

#  Créer le modèle des autres tables
