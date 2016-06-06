import requests
import logging
from os import path

from baleen.utils import file_list, make_dir

log = logging.getLogger(__name__)

# silence request logging
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
    logging.WARNING)


def query_solr(solr_url, core, doi, fields=[]):
    url = '/'.join([solr_url.rstrip('/'), core, 'select'])
    params = {'q': 'doi:"' + doi + '"',
              'wt': 'json'}

    if fields:
        params['fl'] = ','.join(f for f in fields)

    response = requests.get(url, params)

    json = response.json()

    if json['response']['docs']:
        return json['response']['docs'][0]
    else:
        log.error('DOI {!r} not found in core {!r}'.format(doi, core))


def get_text(core, doi, fields, hash_tags, resume, solr_url, text_dir):
    prefix, suffix = doi.split('/')
    text_fname = '#'.join([prefix, suffix] + hash_tags) + '.txt'
    out_dir = path.join(text_dir, prefix)
    text_path = path.join(out_dir, text_fname)

    if resume and path.exists(text_path):
        log.info('skipping file {!r} because it exists'.format(text_path))
    else:
        doc = query_solr(solr_url, core, doi, fields)
        values = []
        for key in fields:
            try:
                val = doc[key]
            except KeyError as key:
                log.error('no {!r} field for doi {!r}'.format(key.args[0], doi))
                return
            # flatten list values, e.g. for fulltext
            if isinstance(val, list):
                values.append('\n'.join(val))
            else:
                values.append(val)
        text = '\n\n'.join(values)
        log.info('creating text file {!r}'.format(text_path))
        try:
            open(text_path, 'w').write(text)
        except:
            make_dir(out_dir)
            open(text_path, 'w').write(text)


def get_texts(doi_files, solr_url, fields, text_dir, hash_tags=[],
              resume=False, max_n=None):
    n = 0

    for doi_fname in file_list(doi_files):
        log.info('getting text sources from {!r}'.format(doi_fname))
        for line in open(doi_fname):
            try:
                core, doi = line.split()
            except:
                log.error('ill-formed line in file {!r}:\n'
                          '{}'.format(doi_fname, line))
                continue

            get_text(core, doi, fields, hash_tags, resume, solr_url, text_dir)
            n += 1
            if n == max_n:
                log.info('reached max_n={}'.format(n))
                break


def get_full_text(doi_files, solr_url, text_dir, hash_tags=['full'],
                  resume=False):
    get_texts(doi_files, solr_url, ['title', 'abstract', 'fulltext'], text_dir,
              hash_tags=hash_tags, resume=resume)


def get_abs_text(doi_files, solr_url, text_dir, hash_tags=['abs'],
                 resume=False, max_n=None):
    """
    get text of abstracts

    :param doi_files:
    :param solr_url:
    :param text_dir:
    :param hash_tags:
    :param resume:
    :return:
    """
    get_texts(doi_files, solr_url, ['title', 'abstract'], text_dir,
              hash_tags=hash_tags, resume=resume, max_n=max_n)
