#! /usr/bin/env python
#coding:utf-8

"""
    External Script to tidy up the example and test centres of the CMIP5 
    questionnaire:
    1. Delete (i.e. set to isDeleted) all grids, platforms, models, simulations 
       from both centres 
    2. Copy HadGEM2-ES model from met office to example centre
    
    TO USE: from cmip5q directory issue:
       > ./py scripts/Tidy_example.py (./py is the local badc directory python)
     
    Author: Gerard Devine, University of Reading
    Date: 12/05/2011
"""

import os
import sys

# putting project and application into sys.path  
sys.path.insert(0, os.path.expanduser('..\protoq'))
sys.path.insert(1, os.path.expanduser('..\..\cmip5q'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#from django.conf import settings #@UnresolvedImport
#logging=settings.LOG

from cmip5q.protoq.models import *


# Settings used within this code
TestCentres = ['1. Example', '2. Test Centre']
SourceCentre = Centre.objects.get(abbrev='MOHC')
TargetCentre = Centre.objects.get(abbrev='1. Example')
SourceModel = 'HadGEM2-ES'


def delElem(elem):
    """
    Sets a passed element, e.g. component/grid to be marked as isDeleted 
    """
    elem.isDeleted = True
    elem.save()


def clearCentre(cent):
    """
    Grab models, grids etc and send them off to be marked isDeleted
    """
    for block in [Component, Grid, Simulation, Platform]:
        elems = block.objects.filter(centre=cent)
        for elem in elems:
            delElem(elem)


def copyToExCen():
    """
    Copy a model from one centre to the example centre
    """ 
    source=Component.objects.filter(abbrev=SourceModel).get(centre=SourceCentre)
    source.copy(TargetCentre)
   

def tidyTestArea():
    """
    Tidy up the test area of the cmip5 questionnaire by:
    1. clearing out all info in test and example centres
    2. copying updated information to example centre
    """
    logging.debug('Beginning tidy-up of test area centres ')
    
    # 1. Delete Example and Test centre information
    for cenabbrev in TestCentres:
        cent = Centre.objects.get(abbrev=cenabbrev)
        clearCentre(cent)

    # 2. Make a copy of official example (Mark Elkington's at this point)
    # TODO: (GD_20110513) Check for uniqueness on the model to be copied
    copyToExCen()
    
    logging.debug('Completed tidy-up of test area centres ')
        
           
if __name__ == '__main__':
    tidyTestArea()

