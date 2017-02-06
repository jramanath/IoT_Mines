# -*- coding: utf-8 -*-
"""
Une vue générique de notre collecteur de données

default_view renvoie le nb de point de mesure actuellement
collecté
"""

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

import logging
import json
import urllib


class Response(HttpResponse):
    """
    Base pour toutes les réponses
    """

    def __init__(self, http_status=200, output=None):

        if output is None:
            output = json.dumps(
                {
                    'nb_point': 0,
                    'execution': 'OK'
                }, ensure_ascii=False, encoding="UTF8")

        logger = logging.getLogger(__name__)
        logger.info("Response: %s", output)

        super(Response, self).__init__(
            output,
            content_type="application/json; charset=utf-8",
            status=http_status,
        )


@csrf_exempt
def default_view(request):
    """
    Renvoyer le nombre de point de mesure
    """
    logger = logging.getLogger(__name__)
    logger.info("%s %s", request.method, urllib.unquote(request.body))

    return Response(output=None)

