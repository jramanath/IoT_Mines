# -*- coding: utf-8 -*-
"""
La vue qui contrôle l'acquisition des données depuis les capteurs
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import logging
import urllib
import json


def init_sensors():
    """
    Une fonction qui doit s'initialiser qu'une seule fois
    """

    logger = logging.getLogger(__name__)

    x = 10
    logger.info(u"On instancie x : %s ", x)

    return x

x = init_sensors()


def default_response(output=None, http_status=200):
    """
    Base de toutes les réponses sur la vue par défaut
    """

    if output is None:
        output = {
            'x': x,
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
    Renvoyer x
    """
    logger = logging.getLogger(__name__)
    logger.info("%s %s", request.method, urllib.unquote(request.body))
    logger.info(u"Lecture de x : %s ", x)

    output = {
        'x': x,
        'execution': 'OK',
    }

    return default_response(output=output)
