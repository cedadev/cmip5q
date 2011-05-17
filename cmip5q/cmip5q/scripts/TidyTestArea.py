#! /usr/bin/env python
#coding:utf-8

"""
    External Script to tidy up the example and test centres of the CMIP5 
    questionnaire:
    1. Delete (i.e. set to isDeleted) all grids, platforms, models, simulations 
       from both centres (**May change this to actual physical delete)
    2. Physically delete refs, files, parties
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
testCentres = ['1. Example', '2. Test Centre']
origCentre = Centre.objects.get(abbrev='MOHC')
targetCentre = Centre.objects.get(abbrev='1. Example')
origPlat = 'IBM Power 6'
origModel = 'HadGEM2-ES'
origSim = 'piControl'


def delElem(elem):
    """
    Sets a passed element, e.g. component/grid to be marked as isDeleted 
    """
    elem.isDeleted = True
    elem.save()


def clearCentre(cent):
    """
    Grab models, grids etc and send them off to be marked isDeleted OR delete
    in situ
    """
    # First those to be marked isDeleted
    for block in [Component, Grid, Simulation, Platform]:
        elems = block.objects.filter(centre=cent)
        for elem in elems:
            delElem(elem)
            
    # Now those that are actually physically deleted
    for block in [Reference, DataContainer, ResponsibleParty]:
        block.objects.filter(centre=cent).delete()


def copyPlatToExCen(sourcePlat):
    """
    Copy a platform from one centre to the example centre
    """
    logging.debug('***** Copying Platform *****')    
    
    p = Platform(abbrev = 'Example Platform',
                 title = 'example centre platform',
                 centre = targetCentre,                              
                 compiler = sourcePlat.compiler,
                 compilerVersion = sourcePlat.compilerVersion,
                 vendor = sourcePlat.vendor,
                 maxProcessors = sourcePlat.maxProcessors,
                 coresPerProcessor = sourcePlat.coresPerProcessor,
                 operatingSystem = sourcePlat.operatingSystem,
                 processor = sourcePlat.processor,
                 interconnect = sourcePlat.interconnect,
                 isDeleted = False,
                 uri = atomuri())
    p.save()
    
    logging.debug('***** Completed Platform copying *****')
    
    
def copyModToExCen(sourceModel):
    """
    Copy a model from one centre to the example centre
    """ 
    logging.debug('Copying Model')    
    
    source = Component.objects.filter(centre=origCentre).get(abbrev=sourceModel)
    source.copy(targetCentre)
    
    logging.debug('***** Completed Model copying *****')


def copySimToExCen(sourcePlat, sourceModel, sourceSim):
    """
    Copy a simulation from one centre to the example centre
    """ 
    s = Simulation(abbrev ='Example_Sim', 
                 title ='Example Simulation', 
                 contact = sourceSim.contact, 
                 author = sourceSim.author, 
                 funder = sourceSim.funder,
                 description = sourceSim.description, 
                 authorList = sourceSim.authorList,
                 uri = atomuri(),
                 experiment = sourceSim.experiment, 
                 numericalModel = sourceSim.numericalModel,
                 ensembleMembers = 1, 
                 platform = sourceSim.platform, 
                 centre = targetCentre)
    s.save()    


def tidyTestArea():
    """
    Tidy up the test area of the cmip5 questionnaire by:
    1. clearing out all info in test and example centres
    2. copying updated information to example centre
    """
    logging.debug('***** START: Beginning tidy-up of test area centres *****')
    
    # 1. Delete Example and Test centre information
    for cenabbrev in testCentres:
        cent = Centre.objects.get(abbrev=cenabbrev)
        clearCentre(cent)

    # 2. Make a copy of official example (Mark Elkington's at this point)
    # TODO: (GD_20110513) Check for uniqueness on the following to be copied
    sourcePlat = Platform.objects.filter(centre=origCentre).get(abbrev=origPlat)
    sourceModel = Component.objects.filter(centre=origCentre).get(abbrev=origModel)
    sourceSim = Simulation.objects.filter(centre=origCentre).get(abbrev=origSim)
    
    copyPlatToExCen(sourcePlat)
    copyModToExCen(sourceModel)
    
    #Now get newly copied model
    exModel = Component.objects.filter(centre=targetCentre, isModel=True, 
                                       isDeleted=False).get(abbrev=origModel+' dup')
    copySimToExCen(sourcePlat, exModel, sourceSim)
    
    logging.debug('***** END: Completed tidy-up of test area centres *****')
        
           
if __name__ == '__main__':
    tidyTestArea()

