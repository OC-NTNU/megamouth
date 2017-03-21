"""
create input for abstracts
"""


import requests
from os import getenv, makedirs
from math import ceil


def create_megamouth_input(core, target, query, num_of_batches=1):
    url = 'http://ocean.idi.ntnu.no:8983/solr/{}/select'.format(core)

    out_dir = '{}/local/inp/{}/{}'.format(getenv('MEGAMOUTH_HOME'), target, core)
    makedirs(out_dir, exist_ok=True)

    step_size = 1000
    start, rows = 0, step_size
    num_found = 0
    n = 0

    max_batch_size = None
    batch_size = 0
    batch_count = 0

    while start <= num_found:
        print('core:{} start:{} end:{}, n:{}'.format(core, start, start + step_size, n))
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
                out_fname = out_dir + '/{}-{}.tsv'.format(core, batch_count)
                print('creating ' + out_fname)
                outf = open(out_fname, 'w')
                batch_size = 0

            doi = doc.get('doi')

            if doi.endswith('/null'):
                # filter out http://dx.doi.org/null
                print('WARNING: skipping ill-formed DOI ' + doi)
                continue

            outf.write('{}\t{}\n'.format(core, doi))
            batch_size += 1
            n += 1

        start += step_size


# elsevier abstracts

query = """
abstract:* AND
-journalname:"New Scientist"
"""

create_megamouth_input(
    'oc-elsevier-art',
    'abs',
    query,
    num_of_batches=8)


# macmillan abstracts

query = """
abstract:* AND (
journalname:"Nature" OR
journalname:"Nature Reviews Microbiology" OR
journalname:"Nature Communications" OR
journalname:"Nature Geoscience" OR
journalname:"Nature Climate Change" OR
journalname:"The ISME Journal" OR
journalname:"Scientific American")
"""

create_megamouth_input(
    'oc-macmillan-art',
    'abs',
    query)


# oxford abstracts

query = """
abstract:*
"""

create_megamouth_input(
     'oc-oxford-art',
     'abs',
     query)

# plos abstracts

query = """
abstract:* AND
journalname:"PLOS Biology"
"""

create_megamouth_input(
     'oc-plos-art',
     'abs',
     query)

# Springer abstracts

query = """
abstract:* AND
-journalname:"The Clinical Investigator"
"""

create_megamouth_input(
     'oc-springer-art',
     'abs',
     query,
    num_of_batches=3)

# Wiley abstracts

query = """
abstract:* AND
-journalname:"Journal of the Science of Food and Agriculture"
-journalname:"Biofuels, Bioproducts and Biorefining"
-journalname:"Pest Management Science"
-journalname:"Transfusion"
-journalname:"Journal of Avian Biology"
-journalname:"Polymer International"
"""

create_megamouth_input(
    'oc-wiley-art',
    'abs',
    query,
    num_of_batches=2)
