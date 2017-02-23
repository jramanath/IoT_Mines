# -*- coding: utf-8 -*-
"""
Variables de configuration et leur valeur par défaut
"""

from collections import OrderedDict


CONSTANCE_CONFIG = OrderedDict([
    # configuration variable for our apps
    # (VARIABLE, (DEFAULT_VALUE, DESCRIPTION, [TYPE])),

    # Collect bucket S3
    ('S3_COLLECT_IN_PROGRESS', (
        False,
        u"Est-ce que la collecte des données S3 est activée ?",
        bool,
    )),
])
