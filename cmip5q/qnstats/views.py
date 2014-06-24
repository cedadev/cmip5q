'''
Created on 15 Nov 2011

@author: gerarddevine
'''

import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext

from cmip5q.protoq.models import CIMObject, Simulation, Component
from cmip5q.qnstats.stats import populate_centre_stats, get_pubs


def numdocs(request):
    '''Returns an xml of number of published docs
    
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
        sim = Simulation.objects.filter(isDeleted=False).get(uri=utdsim)
        simcentres.append(sim.centre)

    numcentsims = set(simcentres)

    #get the number of centres with at least one model published
    modcentres = []
    for utdmod in utdmods:
        mod = Component.objects.filter(isDeleted=False).get(uri=utdmod)
        modcentres.append(mod.centre)

    numcentmods = set(modcentres)

    context = {'numallsims': len(allsims),
               'numutdsims': len(utdsims),
               'numallmods': len(allmods),
               'numutdmods': len(utdmods),
               'numcentsims': len(numcentsims),
               'numcentmods': len(numcentmods),
               }

    return render_to_response('qnstats/apinumdocs.html', context,
                              context_instance=RequestContext(request),
                              mimetype='application/xml')


def stats_summary(request):
    '''Generates current questionnaire statistics
    
    - date/time that statistics were generated
    - total number of simulations published across all centres
    - total number of models published across all centres
    - statistics at each centre level     
    '''
    
    date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    total_pub_sims = get_pubs(cimtype='simulation')
    total_pub_mods = get_pubs(cimtype='component')    
    centre_stats = populate_centre_stats()       
    
    context = {'date_created': date_created, 
               'total_pub_sims': len(total_pub_sims),
               'total_pub_mods': len(total_pub_mods), 
               'centre_stats': centre_stats}

    return render_to_response('qnstats/stats.html', context,
                              context_instance=RequestContext(request))
    
    