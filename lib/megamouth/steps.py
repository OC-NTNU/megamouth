from argh import arg
from baleen.arghconfig import docstring

from megamouth.text import get_abs_text, get_solr_sources


@docstring(get_abs_text)
@arg('-t', '--hash_tags', type=list, action='append')
@arg('-m', '--max_n', type=int)
def get_abs(doi_files, solr_url, text_dir, hash_tags=['abs'],
            resume=False, max_n=None):
    get_abs_text(doi_files, solr_url, text_dir, hash_tags=hash_tags,
                 resume=resume, max_n=max_n)


@arg('xml-files', help='article sources in XMl format from IR step')
@arg('in_dir', help='directory for input files')
def get_inp(xml_files, in_dir):
    '''
    get input (Solr core & DOI pairs)
    '''
    get_solr_sources(xml_files, in_dir)
