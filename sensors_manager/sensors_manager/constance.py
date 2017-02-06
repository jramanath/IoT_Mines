# -*- coding: utf-8 -*-
"""
Variables de configuration et leur valeur par défaut
"""

from collections import OrderedDict


CONSTANCE_CONFIG = OrderedDict([
    # configuration variable for our apps
    # (VARIABLE, (DEFAULT_VALUE, DESCRIPTION, [TYPE])),

    # Collect bucket S3
    ('COLLECT_S3_IN_PROGRESS', (
        False,
        u"Est-ce que la synchro automatique est activée ?",
        bool,
    )),
])
