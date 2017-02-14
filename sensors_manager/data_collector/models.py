# -*- coding: utf-8 -*-
"""
Modèle des données du projet
"""
from __future__ import unicode_literals

from django.db import models
from django_pandas.managers import DataFrameManager
from django.utils import timezone


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

    id = models.AutoField(primary_key=True)
    #date et heure
    datetime = models.DateTimeField(auto_now=False, auto_now_add=False)
    #temperature en degres celsius
    Temperature = models.DecimalField(max_digits=4, decimal_places=2)
    # humidite en pourcentage
    RH = models.DecimalField(max_digits=4, decimal_places=2)
    #luminosite
    Illum = models.DecimalField(max_digits=6, decimal_places=2)
    #code du capteur
    ID = models.CharField(max_length=100, blank=True, null=True)

class DataCapteursFenetres(models.Model):

    id = models.AutoField(primary_key=True)
    #date et heure
    datetime = models.DateTimeField(auto_now=False, auto_now_add=False)
    windows_state = models.BooleanField()







#  Créer le modèle des autres tables
