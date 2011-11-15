'''
Created on 15 Nov 2011

@author: gerarddevine
'''

from django.shortcuts import render_to_response
from django.template import RequestContext

from cmip5q.protoq.models import *


def numdocs(request, docType):
    '''
    gets the current number of published documents for a given doctype
    '''
    
    currentdocs = Simulation.objects.all()
    context = { 'docs': currentdocs }
    return render_to_response('api/apinumdocs.html', context, 
                              context_instance=RequestContext(request), 
                              mimetype='application/xml')