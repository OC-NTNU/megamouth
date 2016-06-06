from argh import arg
from baleen.arghconfig import docstring

from megamouth.text import get_abs_text


@docstring(get_abs_text)
@arg('-t', '--hash_tags', type=list, action='append')
@arg('-m', '--max_n', type=int)
def get_abs(doi_files, solr_url, text_dir, hash_tags=['abs'],
            resume=False, max_n=None):
    get_abs_text(doi_files, solr_url, text_dir, hash_tags=hash_tags,
                 resume=resume, max_n=max_n)
