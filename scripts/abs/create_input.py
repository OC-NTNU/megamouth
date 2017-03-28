#!/usr/bin/env python

"""
create input for abstracts
"""

from megamouth.text import create_megamouth_input

# elsevier abstracts

query = """
abstract:* AND
-journalname:"New Scientist"
"""

create_megamouth_input('abs', 'elsevier', query, num_of_batches=8)


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

create_megamouth_input('abs', 'macmillan', query)


# oxford abstracts

query = """
abstract:*
"""

create_megamouth_input('abs', 'oxford', query)

# plos abstracts

query = """
abstract:* AND
journalname:"PLOS Biology"
"""

create_megamouth_input('abs', 'plos', query)

# Springer abstracts

query = """
abstract:* AND
-journalname:"The Clinical Investigator"
"""

create_megamouth_input('abs', 'springer', query, num_of_batches=3)

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

create_megamouth_input('abs', 'wiley', query, num_of_batches=2)
