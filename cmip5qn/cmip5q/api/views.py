'''
Created on 15 Nov 2011

@author: gerarddevine
'''

from django.shortcuts import render_to_response
from django.template import RequestContext

from cmip5q.protoq.models import CIMObject, Simulation, Component


def numdocs(request, cimtype=None):
    '''
    gets numbers of published documents
    '''
    
    # get number of all documents for particular cim types
    allsims = CIMObject.objects.filter(cimtype="simulation")
    allmods = CIMObject.objects.filter(cimtype="component")
    
    # get only most up-to-date versions
    utdsims = allsims.values_list('uri', flat=True).distinct()
    utdmods = allmods.values_list('uri', flat=True).distinct()
    
    #get the number of centres with at least one simulation published
    simcentres = []
    for utdsim in utdsims:
        sim = Simulation.objects.filter(isDeleted=False).get(
                                                            uri=utdsim)
        simcentres.append(sim.centre)
        
    numcentsims = set(simcentres)
    
    #get the number of centres with at least one model published
    modcentres = []
    for utdmod in utdmods:
        mod = Component.objects.filter(isDeleted=False).get(
                                                            uri=utdmod)
        modcentres.append(mod.centre)
        
    numcentmods = set(modcentres)
    
    context = { 'numallsims': len(allsims),
                'numutdsims': len(utdsims),
                'numallmods': len(allmods), 
                'numutdmods': len(utdmods), 
                'numcentsims': len(numcentsims), 
                'numcentmods': len(numcentmods), 
                }
    
    return render_to_response('api/apinumdocs.html', context, 
                              context_instance=RequestContext(request), 
                              mimetype='application/xml')