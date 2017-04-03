# -*- coding: utf-8 -*-
"""
Scrip contenant quelques fonctions utiles
"""

import os
import logging
import glob
import gzip
import shutil
from logging.handlers import TimedRotatingFileHandler


class TimedCompressedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Extended version of TimedRotatingFileHandler
    that compress logs on rollover.
    """

    def doRollover(self):
        """
        Do a rollover; in this case, a date/time stamp is appended to the
        filename when the rollover happens.

        All preceding log files are automatically gzipped, if need be
        """
        super(TimedCompressedRotatingFileHandler, self).doRollover()

        logger = logging.getLogger(__name__)

        # list the previous log that need compressing
        for old_log in glob.glob(self.baseFilename + ".*"):
            if old_log.endswith('.gz'):
                # old log is already compressed
                continue

            # otherwise, copy the content to a gz file
            with open(old_log, 'rb') as f_in:
                with gzip.open(old_log + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # and remove the old log file
            os.remove(old_log)

