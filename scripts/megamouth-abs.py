#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

from baleen.pipeline import script
from baleen.steps import core_nlp

from megamouth.steps import get_abs

script(steps=[get_abs, core_nlp],
       optional=[],
       default_cfg_fnames=['megamouth.ini', 'local.ini'],
       default_section='ABS')
