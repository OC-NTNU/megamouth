from math import ceil
from os import getenv, makedirs

import requests
import logging
from path import Path

from baleen.utils import file_list, quote_doi, derive_path, remove_any

log = logging.getLogger(__name__)

# silence request logging
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
    logging.WARNING)


class DOIError(Exception):
    pass


def query_solr(session, solr_url, core, doi, fields=[]):
    url = '/'.join([solr_url.rstrip('/'), core, 'select'])
    params = {'q': 'doi:"' + doi + '"',
              'wt': 'json'}

    if fields:
        params['fl'] = ','.join(f for f in fields)

    response = session.get(url, params=params)
    json = response.json()

    if json['response']['docs']:
        return json['response']['docs'][0]

    # TODO: remove hack
    #  *** HACK ***
    # Doi field in Solr records sometimes contains the url to resolve the doi,
    # e.g. http://dx.doi.org/10.1007/s13762-014-0657-1
    # So we try again with the url...
    params['q'] = 'doi:"http://dx.doi.org/{}"'.format(doi),

    response = session.get(url, params=params)
    json = response.json()

    if json['response']['docs']:
        return json['response']['docs'][0]

    log.error('DOI {!r} not found in core {!r}'.format(doi, core))
    raise DOIError()


def get_text(session, core, doi, fields, hash_tags, resume, solr_url, text_dir):
    if doi.startswith('http://dx.doi.org/'):
        doi = doi[18:]
    quoted_doi = quote_doi(doi)
    text_path = derive_path('', new_dir=text_dir, new_corename=quoted_doi, new_ext='txt', append_tags=hash_tags)

    if resume and text_path.exists():
        log.info('skipping file {!r} because it exists'.format(text_path))
    else:
        doc = query_solr(session, solr_url, core, doi, fields)
        values = []
        for key in fields:
            try:
                val = doc[key]
            except KeyError as key:
                log.error('no {!r} field for doi {!r} in core {!r}'.format(key.args[0], doi, core))
                return
            # flatten list values, e.g. for fulltext
            if isinstance(val, list):
                values.append('\n'.join(val))
            else:
                values.append(val)
        text = '\n\n'.join(values)
        log.info('creating text file {!r}'.format(text_path))
        text_path.write_text(text)


def get_texts(doi_files, solr_url, fields, text_dir, hash_tags=[],
              resume=False, max_n=None):
    Path(text_dir).makedirs_p()
    n = 0

    # Use session to deal with the following exception when running many instances in parallel:
    #
    # NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7efc8e600668>:
    # Failed to establish a new connection: [Errno 99] Cannot assign requested address',)
    #
    # See http://stackoverflow.com/questions/30943866/requests-cannot-assign-requested-address-out-of-ports
    with requests.Session() as session:
        for doi_fname in file_list(doi_files):
            log.info('getting text sources from {!r}'.format(doi_fname))
            for line in open(doi_fname):
                try:
                    core, doi = line.split()
                except ValueError:
                    log.error('ill-formed line in file {!r}:\n'
                              '{}'.format(doi_fname, line))
                    continue

                try:
                    get_text(session, core, doi, fields, hash_tags, resume, solr_url, text_dir)
                except DOIError:
                    continue

                n += 1
                if n == max_n:
                    log.info('reached max_n={}'.format(n))
                    break


def get_full_text(doi_files, solr_url, text_dir, hash_tags=['full'],
                  resume=False, max_n=None):
    """
    Get full text of articles

    Parameters
    ----------
    doi_files
    solr_url
    text_dir
    hash_tags
    resume
    max_n

    Returns
    -------

    """
    get_texts(doi_files, solr_url, ['fulltext'], text_dir,
              hash_tags=hash_tags, resume=resume, max_n=max_n)


def get_abs_text(doi_files, solr_url, text_dir, hash_tags=['abs'],
                 resume=False, max_n=None):
    """
    Get abstracts of artciles

    Parameters
    ----------
    doi_files
    solr_url
    text_dir
    hash_tags
    resume
    max_n

    Returns
    -------

    """
    get_texts(doi_files, solr_url, ['title', 'abstract'], text_dir,
              hash_tags=hash_tags, resume=resume, max_n=max_n)


def get_solr_sources(xml_files, in_dir):
    """
    Convert output of IR step (article sources in XMl format)
    to Megamouth input files (tab-separated text file where each line contains
    the name of a Solr core and the DOI of a source article).
    """
    in_dir = Path(in_dir)
    in_dir.makedirs_p()

    for xml_file in file_list(xml_files):
        name = Path(xml_file).name
        # arbitrary mapping from filenames to Solr cores
        if name.startswith('elsevier'):
            core = 'oc-elsevier-art'
        elif name.startswith('macmillan'):
            core = 'oc-macmillan-art'
        elif name.startswith('wiley'):
            core = 'oc-wiley-art'
        elif name.startswith('springer'):
            core = 'oc-springer-art'
        else:
            raise ValueError('undefined core for file ' + xml_file)

        tsv_file = in_dir + '/' + Path(xml_file).name + '.tsv'

        # XML is ill-formed (incomplete entities etc.)
        # so do not use an XML parser
        with open(xml_file) as inf, open(tsv_file, 'w') as outf:
            log.info('creating ' + tsv_file)

            for line in inf:
                if line.lstrip().startswith('<doi>'):
                    doi = '/'.join(line.split('<')[-2].split('/')[-2:])
                    print(core, doi, sep='\t', file=outf)


def create_megamouth_input(corpus, segment, query, num_of_batches=1):
    core = 'oc-{}-art'.format(segment)
    url = 'http://ocean.idi.ntnu.no:8983/solr/{}/select'.format(core)

    step_size = 1000
    start, rows = 0, step_size
    num_found = 0
    n = 0

    max_batch_size = None
    batch_size = 0
    batch_count = 0
    dois = set()
    duplicates = 0
    no_doi = 0
    ill_formed = 0

    while start <= num_found:
        print('segment:{} start:{} end:{}, n:{}'.format(segment, start, start + step_size, n))
        params = {'q': query,
                  'start': start,
                  'rows': rows,
                  'wt': 'json',
                  'fl': 'doi'}

        response = requests.get(url, params)
        json_response = response.json()
        num_found = json_response['response']['numFound']
        if not max_batch_size:
            max_batch_size = ceil(num_found / num_of_batches)

        for doc in json_response['response']['docs']:
            if batch_count == 0 or batch_size == max_batch_size:
                batch_count += 1

                out_dir = '{}/local/inp/{}/{}-{}'.format(getenv('MEGAMOUTH_HOME'), corpus, segment, batch_count)
                # remove old files to prevent left-overs
                remove_any(out_dir)
                makedirs(out_dir, exist_ok=True)

                out_fname = out_dir + '/{}-{}.tsv'.format(segment, batch_count)
                print('creating ' + out_fname)
                outf = open(out_fname, 'w')
                batch_size = 0

            doi = doc.get('doi')

            if doi in dois:
                print('WARNING: skipping duplicate DOI ' + doi)
                duplicates += 1
            elif not doi:
                print('WARNING: skipping entry without DOI: {}'.format(doc))
                no_doi += 1
            elif doi.endswith('/null'):
                # filter out http://dx.doi.org/null
                print('WARNING: skipping ill-formed DOI ' + doi)
                ill_formed += 1
            else:
                outf.write('{}\t{}\n'.format(core, doi))
                dois.add(doi)
                batch_size += 1
                n += 1

        start += step_size

    print('SUMMARY: {}\n#valid DOI: {}\n#duplicate DOI: {}\n#no DOI: {}\n#ill-formed DOI: {}'.format(
        segment, n, duplicates, no_doi, ill_formed))