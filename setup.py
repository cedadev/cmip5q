#!/usr/bin/env python
"""Distribution Utilities setup program for Metafor Questionnaire

Metafor Project
"""
__author__ = "B N Lawrence"
__date__ = "09/11/17"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Bryan.Lawrence@stfc.ac.uk"
__revision__ = '$Id$'

# Bootstrap setuptools if necessary.
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
import os

_longDescription = """Django web application for CMIP5 questionnaire

To set-up, run:

$ ./setupProto.sh

from this directory to initialise the SQLite Database.  This uses the 'python'
executable in your PATH variable.  To set an alternative python, set the 
PYTHON environment variable e.g.

$ export PYTHON=python2.5
$ ./setupProto.sh

Then to run the application,

$ python manage.py runserver

The wsgi package contains settings to run the application using paster e.g.

$ paster serve service.ini

The service.ini provides example code for securing the application with NDG
Security and should be modified to suit
"""

setup(
    name =                   'cmip5q',
    version =                '1.7.1',
    description =            'CMIP5 Questionnaire',
    long_description =       _longDescription,
    author =                 'Bryan Lawrence',
    author_email =           'Bryan.Lawrence@stfc.ac.uk',
    maintainer =             'Bryan Lawrence',
    maintainer_email =       'Bryan.Lawrence@stfc.ac.uk',
    url =                    'http://metaforclimate.eu/trac',
    license =                'BSD - See LICENCE file for details',
    install_requires =       ['django','lxml','simplejson'],
    packages =               find_packages(),
    package_data = {
        'cmip5q': ['000Issues', 'LICENSE', 'loadmm', '*.xml', 
            'data/experiment/*.xml', 'data/model/*.xml', 
            'setupProto.sh','vocabs/*.xml'
        ],
        'test.data': ['*'], 
        'test.integration.wsgi.paste': ['README', '*.ini'],
        'test.integration.wsgi.secured': [
            'README', '*.ini', '*.xml',
            'ca/*.0', 'ca/*.crt', 'pki/*.crt', 'pki/*.key'
        ],
    },
    include_package_data =    True,
    zip_safe =                False
)
