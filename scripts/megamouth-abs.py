#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

from baleen.pipeline import script
from baleen.steps import core_nlp, lemma_trees, ext_vars, offsets, prep_vars, \
    prune_vars, clean

from megamouth.steps import get_abs

script(steps=[get_abs, core_nlp, lemma_trees, ext_vars, offsets, prep_vars,
              prune_vars],
       optional=[clean],
       default_cfg_fnames=['megamouth.ini', 'local.ini'],
       default_section='ABS')
