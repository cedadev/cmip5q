'''
Created on 14 Sep 2012

@author: gerarddevine
'''
from django.db.models import Q

from cmip5q.protoq.models import *
from helpers import *


def unpub_mods_errors(centre):
    '''Returns completeness/errors of a model that has not yet been published
    
    '''
    
    # get all non-isDeleted components where isModel = true for given centre
    mods = Component.objects.filter(centre=centre, isModel=True, isDeleted=False)
    
    # exclude those where the uuid is in CIMobects (cimtype = component)
    mods_exc1 = mods.exclude(uri__in = CIMObject.objects.filter(cimtype='component').values_list('uri', flat=True) )
    #exclude those that are dummy models
    mods_exc2 = mods_exc1.exclude(abbrev__in = ['Model Template dup', 'Model Template dupcp' ])
    mods_exc3 = mods_exc2.exclude(abbrev__endswith='cp')
    mods_exc4 = mods_exc3.exclude(reduce(lambda x, y: x | y, (Q(abbrev__icontains=x) for x in ['delete', 'zzz', 'backup'])))


    #mods_exc4 = mods_exc3.exclude(abbrev__icontains=['delete', 'zzz', 'backup'])
            
    # return the validation stats for each model
    unpubmodels = []
    for mod in mods_exc4:
        # run the models own validation function
        mod.validate()
        # store the validation stats 
        moddetail = {'modelname': mod.abbrev, 
                          'numchecks': mod.numberOfValidationChecks, 
                          'numerrors': mod.validErrors}
                          
        unpubmodels.append(moddetail)
    
    return unpubmodels
           
    
def get_pubs(cimtype, centre=None):
    '''Returns the number of cim documents published
    
    - cimtype : define cim document type
    - centre : define centre. If centre is not supplied, the number of 
               documents across all centres will be returned.
    
    '''
       
    #filter by centre if provided
    if centre != None:
        pub_docs = CIMObject.objects.filter(cimtype=cimtype)
        
        uri_list = []
        for doc in pub_docs:
            uri_list.append(doc.uri)
        
        if cimtype == 'component':    
            pub_docs = Component.objects.filter(centre=centre, isModel=True, isDeleted=False, uri__in=uri_list)
        elif cimtype == 'simulation':
            pub_docs = Simulation.objects.filter(centre=centre, isDeleted=False, uri__in=uri_list)
    
    else:
        # return number of docs for all centres
        pub_docs = CIMObject.objects.filter(cimtype=cimtype)
        # filter only most up-to-date versions
        pub_docs = pub_docs.values_list('uri', flat=True).distinct()
    
            
    return pub_docs 


def populate_centre_stats():
    '''function to populate centres stats table
    
    Returns (for each centre):
    - Institution
    - Number of existing simulations
    - Number of published simulations
    - Number of existing models
    - Number of published models
    - Names of published models
    - Completeness of unpublished models
    '''
    
    centre_stats = []
    
    #get all centres
    centres = cmip5_centres()
    
    for centre in centres:
        #get simulations in existance by centre
        sims = Simulation.objects.filter(centre=centre, isDeleted=False)
        #get simulations published by centre
        simspub = get_pubs(cimtype='simulation', centre=centre)
        #get components in existance by centre
        mods = Component.objects.filter(centre=centre, isModel=True, isDeleted=False)
        #filter out dummy models
        mods_exc2 = mods.exclude(abbrev__in=['Model Template dup', 'Model Template dupcp' ])
        mods_exc3 = mods_exc2.exclude(abbrev__endswith='cp')
        mods_exc4 = mods_exc3.exclude(reduce(lambda x, y: x | y, (Q(abbrev__icontains=x) for x in ['delete', 'zzz', 'backup'])))
        #mods = mods.exclude(abbrev__icontains=['delete', 'zzz', 'backup'])
        #get models published by centre
        modspub = get_pubs(cimtype='component', centre=centre)
        #get completeness of unpublished models
        unpub_mods = unpub_mods_errors(centre=centre) 
        
        stat = {'centrename':centre.abbrev,
                'numsims':len(sims), 
                'numsimspub':len(simspub), 
                'nummods': len(mods_exc4),
                'nummodspub': len(modspub), 
                'modslist': modspub,
                'unpubmods': unpub_mods}
        
        centre_stats.append(stat)
    
    return centre_stats
