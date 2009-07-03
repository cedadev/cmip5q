# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import PropertyForm, tabs
from cmip5q.protoq.components import componentHandler
from cmip5q.protoq.simulations import simulationHandler
from cmip5q.XMLVocabReader import XMLVocabReader
from django import forms
import uuid
import logging

MESSAGE=''

def index(request):
    #find all the centre objects
    centre_list=Centre.objects.all()
    #get a template
    t=loader.get_template('default.html')
    f=CentreForm() 
    #put some stuff into the template
    c=Context({'centre_list':centre_list,'cf':f})
    return HttpResponse(t.render(c))
   
def centres(request):
    ''' For choosing amongst centres '''
    p=Centre.objects.all()
    if request.method=='POST':
        #yep we've selected something
        try:
            selected_centre=p.get(pk=request.POST['choice'])
        except KeyError:
            #redisplay form
            return render_to_response('centres.html',
                {'centreList':p})
        return HttpResponseRedirect(reverse('cmip5q.protoq.views.centre',args=(selected_centre.id,))) 
    else: 
        logging.info('Viewing centres')
        return render_to_response('centres.html',{'centreList':p})
    
def centre(request,centre_id):
    ''' Handle the top page on a centre by centre basis '''
    c=Centre.objects.get(pk=centre_id)
    models=[]
    models=[Component.objects.get(pk=m.id) for m in c.component_set.filter(scienceType='model')]
    #monkey patch the urls to edit these ...
    for m in models:
        m.url=reverse('cmip5q.protoq.views.componentEdit',args=(c.id,m.id))
    platforms=[Platform.objects.get(pk=p['id']) for p in c.platform_set.values()]
    for p in platforms:
        p.url=reverse('cmip5q.protoq.views.platformEdit',args=(c.id,p.id))
    sims=Simulation.objects.filter(centre=c.id)
    for s in sims:
        s.url=reverse('cmip5q.protoq.views.simulationEdit',args=(c.id,s.id))
    
    newmodURL=reverse('cmip5q.protoq.views.componentAdd',args=(c.id,))
    newplatURL=reverse('cmip5q.protoq.views.platformAdd',args=(c.id,))
    viewsimURL=reverse('cmip5q.protoq.views.simulationList',args=(c.id,))
    
    
    logging.info('Viewing %s'%c.id)
    return render_to_response('centre.html',
        {'centre':c,'models':models,'platforms':platforms,
        'newmod':newmodURL,'newplat':newplatURL,'sims':sims,'viewsimurl':viewsimURL,
        'tabs':tabs(c.id,'Summary'),'notAjax':not request.is_ajax()})
        
        
#### CONFORMANCE HANDLING ###########################################################
def conformanceEdit(request,cen_id,sim_id,req_id):
    ''' Handle a specific conformance within a simulation '''
    return HttpResponse('Not implemented')
        
#### COMPONENT HANDLING ###########################################################

# Provide a vew interface to the component object 
def componentAdd(request,centre_id):
    ''' Add a component '''
    c=componentHandler(centre_id)
    return c.add()
    
def componentEdit(request,centre_id,component_id):
    ''' Edit a component '''
    c=componentHandler(centre_id,component_id)
    return c.edit(request)
    
def componentSub(request,centre_id,component_id):
    ''' Add a subcomponent onto a component '''
    c=componentHandler(centre_id,component_id)
    return c.addsub()
    
def componentRefs(request,centre_id,component_id):
    ''' Manage the references associated with a component '''
    c=componentHandler(centre_id,component_id)
    return c.manageRefs(request)
    
def componentValidate(request,centre_id,component_id):
    ''' Validate a component against whatever rules we develop '''
    c=componentHandler(centre_id,component_id)
    return c.validate()
    
def componentView(request,centre_id,component_id):
    ''' View a version of the component description "nicely" laid out'''
    c=componentHandler(centre_id,component_id)
    return c.view()
    
def componentXML(request,centre_id,component_id):
    ''' Return an xml version of the component '''
    c=componentHandler(centre_id,component_id)
    return c.xml()
  
   
###### REFERENCE HANDLING ######################################################
   
def references(request):
    ''' Handle the listing of references '''
    refs=Reference.objects.all()
    return render_to_response('references.html',{'refs':refs})

def addReference(request,component_id=None):
    ''' Handle the addition of a new reference, if componentID is present, offer to 
    return to their, otherwise go back to references '''
    logging.debug('Adding reference to %s'%component_id)
    if component_id is not None:
        url=reverse('cmip5q.protoq.views.addReference',args=(component_id,))
    else: url=reverse('cmip5q.protoq.views.addReference')
    
    if request.method=='POST':
        rform=ReferenceForm(request.POST)
        if rform.is_valid():
            ref=rform.save()
            c=Component.objects.get(pk=component_id)
            c.references.add(ref)
            c.save()
            logging.info('Added reference %s to component %s'%(ref.id,c.id))
            if component_id is None:
                return HttpResponseRedirect(reverse('cmip5q.protoq.views.references'))
            else:
                return HttpResponseRedirect(reverse('cmip5q.protoq.views.componentRefs',args=(component_id,)))
        else:
            print rform.errors
    else:
        rform=ReferenceForm()
    return render_to_response('reference.html',{'rform':rform,'url':url,'label':'add','notAjax':not request.is_ajax()})
        
def editReference(request,reference_id):
    r=Reference.objects.get(pk=reference_id)
    if request.method=='POST':
        rform=ReferenceForm(request.POST,instance=r)
        if rform.is_valid():
            rform.save()
            return HttpResponseRedirect(reverse('cmip5q.protoq.views.references'))
    else:
        rform=ReferenceForm(instance=r)
    url='/cmip5/references/edit/%s/'%reference_id
    return render_to_response('reference.html',{'rform':rform,'url':url,'label':'update','notAjax':not request.is_ajax()})
    
def assignReference(request,component_id,reference_id):
    ''' Make the link between a reference and a component '''
    url=reverse('cmip5q.protoq.views.componentRefs',args=(component_id,))
    try:
        c=Component.objects.get(pk=component_id)
        r=Reference.objects.get(pk=reference_id)
    except:
        message="Unable to handle component %s and/or reference %s"%(component_id,reference_id)
        return render_to_response('error.html',{'message':message,'url':url})
    c.references.add(r)
    c.save()
    return HttpResponseRedirect(url)

def remReference(request,component_id,reference_id):
    ''' Break link between a reference and a specific component '''
    url=reverse('cmip5q.protoq.views.componentRefs',args=(component_id,))
    try:
        c=Component.objects.get(pk=component_id)
        r=Reference.objects.get(pk=reference_id)
    except:
        message="Unable to handle component %s and/or reference %s"%(component_id,reference_id)
        return render_to_response('error.html',{'message':message,'url':url})
    c.references.remove(r)
    c.save()
    return HttpResponseRedirect(url)

    
###### SIMULATION HANDLING ######################################################

def simulationEdit(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simid=simulation_id)
    return s.edit(request)

def simulationAdd(request,centre_id,experiment_id):
    s=simulationHandler(centre_id,expid=experiment_id)
    return s.add(request)

def simulationValidate(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simid=simulation_id)
    return s.validate()

def simulationView(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simid=simulation_id)
    return s.view()

def simulationList(request,centre_id):
    s=simulationHandler(centre_id)
    return s.list(request)
    
        
##### PLATFORM HANDLING ###########################################################
# we can do this simply because p doesn't have any mandatory links.

def platformAdd(request,centre_id):
    ''' Add a new platform to a centre '''
    u=str(uuid.uuid1())
    p=Platform(centre=Centre.objects.get(pk=centre_id),uri=u,title='abcd',abbrev='abcd')
    p.save()
    return HttpResponseRedirect(
        reverse('cmip5q.protoq.views.platformEdit',args=(centre_id,p.id,)))
        
def platformEdit(request,centre_id,platform_id):
    ''' Handle platform editing '''
    p=Platform.objects.get(pk=platform_id)
    if request.method=='POST':
        pform=PlatformForm(request.POST,instance=p)
        if pform.is_valid():
            pform.save()
            return HttpResponseRedirect(
                reverse('cmip5q.protoq.views.centre',args=[p.centre_id,]))
    else:
        pform=PlatformForm(instance=p)
    url=reverse('cmip5q.protoq.views.platformEdit',args=(p.centre_id,p.id,))
    return render_to_response('platform.html',
                {'pform':pform,'centre_id':p.centre_id,'platform_id':p.id,
                'url':url})
        
########## EXPERIMENT VIEWS ##################
    
def viewExperiment(request,experiment_id):
    e=Experiment.objects.get(pk=experiment_id)
    r=e.requirements.all()
    return render_to_response('experiment.html',{'e':e,'reqs':r,'notAjax':not request.is_ajax()})
    
    
    