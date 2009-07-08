"""Module for enabling the Django application to run in a WSGI environment

Metafor Project

"""
__author__ = "P J Kershaw"
__date__ = "08/07/07"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id$"

import django.core.handlers.wsgi

def app_factory(globalConfig, **localConfig):
    '''Paste app factory wrapper for Django WSGI handler.  This enables the 
    Django application to be added as an app entry in a Paste ini file e.g.
       
    [app:CMIP5QApp]
    paste.app_factory = wsgi:app_factory
    '''
    return django.core.handlers.wsgi.WSGIHandler()