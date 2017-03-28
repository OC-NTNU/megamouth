#!/usr/bin/env python

"""
process all abstracts
"""

from os import getenv

from baleen.pipeline import script
from baleen.steps import *
from megamouth.steps import clean_all

script(steps=[
        uniq,
        setup_server,
        multi_toneo,
        ppgraph],
    optional=[
        start_server,
        stop_server,
        report,
        clean,
        clean_cache],
    default_cfg_fnames=[
        getenv('MEGAMOUTH_HOME') + '/scripts/megamouth.ini',
        getenv('MEGAMOUTH_HOME') + '/scripts/abs/megamouth-abs.ini',
        getenv('MEGAMOUTH_HOME') + '/scripts/local.ini'])
