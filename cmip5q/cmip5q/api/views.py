'''
Created on 15 Nov 2011

@author: gerarddevine
'''

from django.shortcuts import render_to_response
from django.template import RequestContext

from cmip5q.protoq.models import CIMObject


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
    
    context = { 'numallsims': len(allsims),
                'numutdsims': len(utdsims),
                'numallmods': len(allmods), 
                'numutdmods': len(utdmods), 
                }
    
    return render_to_response('api/apinumdocs.html', context, 
                              context_instance=RequestContext(request), 
                              mimetype='application/xml')