'''
Created on 5 Sep 2011

@author: gerarddevine
'''

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse

from cmip5q.protoq.admin.admin_forms import CompCopyForm
from cmip5q.protoq.admin.admin_scripts import copyCompToNewCen

from cmip5q.protoq.models import Component, Centre


def modelcopy(request):
    '''
    controller for cross-centre model copying in admin 
    '''
        
    # Deal with response 
    if request.method == 'POST':
        sourcemodel=Component.objects.get(id=request.POST['sourcemodel'])
        targetcentre=Centre.objects.get(id=request.POST['targetcentre'])
        
        copyCompToNewCen(sourcemodel, targetcentre)        
        return HttpResponse("Successfully Copied") # Redirect to success page
    else:
        form = CompCopyForm() # An unbound form
    
    return render_to_response("admin/protoq/Component/compcopy.html",
                              {'form' : form},
    )