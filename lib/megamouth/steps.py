from argh import arg
from baleen.arghconfig import docstring

from megamouth.text import get_abs_text


@docstring(get_abs_text)
@arg('--hash_tags', type=list, action='append')
def get_abs(doi_files, solr_url, text_dir, hash_tags=['abs'],
            resume=False):
    get_abs_text(doi_files, solr_url, text_dir, hash_tags=hash_tags,
                 resume=resume)
