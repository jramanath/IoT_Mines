# -*- coding: utf-8 -*-
"""
Scrip contenant quelques fonctions utiles
"""

import os
import logging
import glob
import gzip
import shutil
import pytz
import tzlocal

from dateutil import tz
from dateutil import parser as dateparser
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

        logger.debug('Waf waf')

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


def is_utc(dt):
    """
    Est-ce que ce datetime est au format UTC ?
    """
    return (dt.tzinfo == tz.tzutc() or
            (dt.tzinfo == tz.tzlocal() and
             tzlocal.get_localzone() == pytz.utc))


def is_naive(dt):
    """
    Est-ce que ce datetime est naif, c'est-à-dire sans time zone ?
    """
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def datetime_format(dt):
    paris_tz = pytz.timezone('Europe/Paris')
    paris_dt = dt.astimezone(paris_tz)
    template = (u"{dt.day:02d}/{dt.month:02d}/{dt.year:04d} "
                u"à {dt.hour}h{dt.minute:02d}")
    return template.format(dt=paris_dt)


def date_format(dt):
    return "{dt.day:02d}/{dt.month:02d}/{dt.year:04d}".format(dt=dt)


parse = dateparser.parse
