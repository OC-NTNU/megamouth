#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

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
              rels2csv,
              setup_server,
              toneo,
              ppgraph],
       optional=[get_inp,
                 remove_server,
                 start_server,
                 stop_server,
                 add_cit,
                 add_meta,
                 clean,
                 clean_cache,
                 report,
                 tag_trees],
       default_cfg_fnames=['megamouth.ini', 'local.ini'],
       default_section='ABS')
