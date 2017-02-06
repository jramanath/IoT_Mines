# -*- coding: utf-8 -*-
"""
Une vue générique de notre collecteur de données

default_view renvoie le nb de point de mesure actuellement collecté
"""

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from data_collector.models import DataTISensor, DataWindowsSensor, DataLoader

import logging
import json
import urllib


def default_response(output=None, http_status=200):
    """
    Base de toutes les réponses sur la vue par défaut
    """

    if output is None:
        output = {
            'nb_fichiers_charges': 0,
            'execution': 'OK',
        }

    output = json.dumps(output, ensure_ascii=False, encoding="UTF8")

    logger = logging.getLogger(__name__)
    logger.info("Response: %s", output)

    response = HttpResponse(output, content_type="application/json; charset=utf-8",
                            status=http_status)

    return response


@csrf_exempt
def default_view(request):
    """
    Renvoyer le nombre de point de mesure
    """
    logger = logging.getLogger(__name__)
    logger.info("%s %s", request.method, urllib.unquote(request.body))

    # compter le nombre de mesures / fichiers chargées
    nb_fichier = DataLoader.objects.count()
    nb_mesures_TI = DataTISensor.objects.count()
    nb_mesures_windows = DataWindowsSensor.objects.count()

    output = {
        'nb_fichiers_charges': nb_fichier,
        'nb_mesures_TI': nb_mesures_TI,
        'nb_mesures_windows': nb_mesures_windows,
        'execution': 'OK',
    }

    return default_response(output=output)

