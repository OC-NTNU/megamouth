#!/usr/bin/env python

"""
process Elsevier abstracts 2
"""

from os import getenv

from baleen.pipeline import script
from baleen.steps import *

from megamouth.steps import get_abs, get_inp

script(steps=[get_abs,
              core_nlp,
              lemma_trees,
              ext_vars,
              offsets,
              prep_vars,
              prune_vars,
              tag_trees,
              ext_rels,
              arts2csv,
              vars2csv,
              rels2csv],
       optional=[get_inp,
                 remove_server,
                 start_server,
                 stop_server,
                 add_cit,
                 add_meta,
                 clean,
                 clean_cache,
                 report,
                 tag_trees,
                 setup_server,
                 toneo,
                 ppgraph],
       default_cfg_fnames=[
           getenv('MEGAMOUTH_HOME') + '/scripts/megamouth.ini',
           getenv('MEGAMOUTH_HOME') + '/scripts/local.ini',
           getenv('MEGAMOUTH_HOME') + '/scripts/abs/wiley/megamouth-abs-wiley-2.ini'],
       default_section='ABS')
