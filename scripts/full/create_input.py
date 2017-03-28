#!/usr/bin/env python

"""
create input for full texts
"""

from megamouth.text import create_megamouth_input

# elsevier full texts

query = """
fulltext:* AND
-journalname:"New Scientist"
"""

create_megamouth_input('full', 'elsevier', query, num_of_batches=8)

# macmillan full texts

query = """
fulltext:* AND (
journalname:"Nature" OR
journalname:"Nature Reviews Microbiology" OR
journalname:"Nature Communications" OR
journalname:"Nature Geoscience" OR
journalname:"Nature Climate Change" OR
journalname:"The ISME Journal" OR
journalname:"Scientific American")
"""

create_megamouth_input('full', 'macmillan', query)

# oxford full texts

query = """
fulltext:*
"""

create_megamouth_input('full', 'oxford', query)

# plos full texts

query = """
fulltext:* AND
journalname:"PLOS Biology"
"""

create_megamouth_input('full', 'plos', query)

# Springer full texts

query = """
fulltext:* AND
-journalname:"The Clinical Investigator"
"""

create_megamouth_input('full', 'springer', query, num_of_batches=3)

# Wiley full texts

query = """
fulltext:* AND
-journalname:"Journal of the Science of Food and Agriculture"
-journalname:"Biofuels, Bioproducts and Biorefining"
-journalname:"Pest Management Science"
-journalname:"Transfusion"
-journalname:"Journal of Avian Biology"
-journalname:"Polymer International"
"""

create_megamouth_input('full', 'wiley', query, num_of_batches=2)
