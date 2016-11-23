#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
if (sys.version_info[0] == 2 and sys.version_info[1] < 7) or (sys.version_info[0] >= 3):
    sys.exit('Python version >= 2.7 and < 3.0')

config = {
    'name': 'taxodb_ncbi',
    'author': 'Corinne Maufrais',
    'version': '1.3.4',
    'author_email': 'corinne.maufrais@pasteur.fr',
    'url': 'https://github.com/C3BI-pasteur-fr/taxodb_ncbi',
    'download_url': 'https://github.com/C3BI-pasteur-fr/taxodb_ncbi',
    'license': 'GPLv3',
    'description': """
                   taxodb_ncbi.py is a simple python script used to format the NCBI taxonomy Database
                   (http://www.ncbi.nlm.nih.gov/taxonomy).
                   It requires bsddb3 (https://pypi.python.org/pypi/bsddb3) python library and Berkeley DB library
                   (http://www.oracle.com) to work.
                   """,
    'package_dir': {'': 'src'},
    'scripts': ['src/taxodb_ncbi.py'],
    'install_requires': ['bsddb3']
}

setup(**config)
