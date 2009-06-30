# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import PropertyForm
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
    platforms=[Platform.objects.get(pk=p['id']) for p in c.platform_set.values()]
    # we need to sort some stuff out to help the template, which as
    # far as I can tell can't access variables via a function call, and
    # nor can it access list members individually.
    exp=[]
    class etmp:
        def __init__(self,abbrev,values,id):
            self.abbrev=abbrev
            self.values=values
            self.id=id
    for e in Experiment.objects.all():
        exp.append(etmp(e.abbrev,[s for s in e.simulation_set.filter(centre=centre_id)],e.id))
    logging.info('Viewing %s'%c.id)
    return render_to_response('centre.html',
        {'centre':c,'experiments':exp,'models':models,'platforms':platforms})
        
        
#### COMPONENT HANDLING ###########################################################

def listComponents(request,centre_id=None):
    ''' List all components, and return to a specific centre'''
    return HttpResponse('Not implemented')

def addSubComponent(request,parent_id,component_type='sub'):
    ''' Add a component to a parent ... '''
    # components/addsub/parent_id/
    # components/addsub/parent_id/component_type|component_id/ (the latter for copy as new)
    parent=Component.objects.get(pk=parent_id)
    centre_id=parent.centre_id
    component=_makeComponent(centre_id,component_type)
    #default should be that children inherit parents contact.
    component.contact=parent.contact
    component.abbrev='unknown'
    component.save()
    parent.components.add(component)
    url=reverse('cmip5q.protoq.views.editComponent',args=(component.id,))
    logging.info('Created subcomponent %s to component %s'%(component.id,parent_id))
    return HttpResponseRedirect(url)

def addComponent(request,centre_id,cmip5=True):
    '''Set up and add a new model (component) at a specific centre, and
    if cmip5 is true, use the controlled vocabularly to setup subtypes '''
    component=_makeComponent(centre_id,scienceType='model')
    author='bnl@foo.bar'  # FIXME
    component.contact=author
    component.title='GCM Template'
    component.abbrev='GCM Template'
    mindmaps=['Atmosphere.xml','Ocean.xml','SeaIce.xml','OceanBioChemistry.xml']
    for m in mindmaps:
        x=XMLVocabReader(m, centre_id,author)
        x.doParse()
        xx=Component.objects.get(pk=x.topLevelID)
        component.components.add(xx)
        #don't know why I have to use the real component instead of ID here.
        logging.debug('Mindmap %s added with component id %s'%(m,x.topLevelID))
    component.save()
    logging.info('Created new component %s in centre %s'%(component.id,centre_id)) 
    for x in component.components.all(): logging.debug('...component includes %s'%x.abbrev)
    return HttpResponseRedirect(reverse('cmip5q.protoq.views.editComponent',args=(component.id,)))

def _makeComponent(centre_id,scienceType='sub'):
    ''' Just make and return a new component instance'''
    centre=Centre.objects.get(pk=centre_id)
    #ok create a new component
    u=str(uuid.uuid1())
    c=Component(scienceType=scienceType,centre=centre,abbrev='',uri=u)
    #now save to database so that we get a primary key value
    c.save()
    logging.info('Created new component %s in centre %s (type %s)'%(c.id,centre_id,scienceType))
    return c

def _deepCopy(centre_id,component_id):
    ''' Create a copy of component_id '''
    #
    # we no longer support the concept of a deep copy ....
    # it's likely to be very model dependent because of the m2m issues ...
    #
    return None

 
def editComponent(request,component_id):
    ''' Provides a form to edit a component, and handle the posting of a form
    containing edits for a component '''
    
    logging.debug('Starting editing component %s'%component_id)
    
    # find my own url ...
    url=reverse('cmip5q.protoq.views.editComponent',args=(component_id,))
    refurl=reverse('cmip5q.protoq.views.addReference',args=(component_id,))
    
    c=Component.objects.get(pk=int(component_id))
    # c.centre already available
    
    # now get parent, if available 
    # and monkey patch it in, all monkey patching to use prefix TC ...
    parent=Component.objects.filter(components=component_id)
    if len(parent)==0: 
        c.TCparentID=None
    else: 
        c.TCparentID=parent[0].id
        c.TCparentAbbrev=parent[0].abbrev
    logging.debug('editing component %s which has parent %s'%(component_id,c.TCparentID))
    # now get subcomponents
    subc=c.components.all()
  
    # this is the automatic machinery ...
    refs=Reference.objects.filter(component__id=component_id)
    
    pform=PropertyForm(c,prefix='props')
    postOK=True
    message=''
    if request.method=="POST":
        cform=ComponentForm(request.POST,prefix='gen',instance=c)
        if cform.is_valid():
            uricopy=c.uri
            c=cform.save(commit=False)
            #these are all the bits not in the form ...
            c.uri=uricopy
            c.save()
            logging.debug('Saving component %s details (e.g. uri %s)'%(c.id,c.uri))
        else:
            logging.debug('Unable to save characteristics for component %s'%component_id)
            postOK=False
            message=cform.errors
        pform.update(request)
    
    # We sepereate the response handling so we can do some navigation in the
    # meanwhile ...
    navtree=yuiTree2(component_id,baseURL=url)
    
    #OK, we have three cases to handle:
    
    #FIXME; we'll need to put this in the right places with instances:
   
    if request.method=='POST':
        if postOK:
            #redirect, so repainting the page doesn't resubmit
            logging.debug('Finished handling post to %s'%component_id)
            return HttpResponseRedirect(url)
        else:
            pass
            # don't reset the forms so the user gets an error response.
    else:
        #get some forms
	cform=ComponentForm(instance=c,prefix='gen')
  
    logging.debug('Finished handling %s to component %s'%(request.method,component_id))
    return render_to_response('componentMain.html',
            {'c':c,'subs':subc,'refs':refs,
            'cform':cform,'pform':pform,
            'm':message,'navtree':navtree.html,'refu':refurl})
            
      
               
def componentRefs(request,component_id):
    ''' Handle references for a specific component '''
    refs=Reference.objects.filter(component__id=component_id)
    allrefs=Reference.objects.all()
    available=[]
    c=Component.objects.get(pk=component_id)
    for r in allrefs: 
        if r not in refs:available.append(r) 
    rform=ReferenceForm()
    refu=reverse('cmip5q.protoq.views.addReference',args=(component_id,))
    baseURLa=reverse('cmip5q.protoq.views.assignReference',args=(1,1,))[0:-4]
    baseURLr=reverse('cmip5q.protoq.views.remReference',args=(1,1,))[0:-4]
    return render_to_response('componentRefs.html',
        {'refs':refs,'available':available,'rform':rform,'c':c,
        'refu':refu,'baseURLa':baseURLa,'baseURLr':baseURLr})
        
#
##
## OBSOLETE compnent CODE FOLLOWS
#
        
def componentSubs(request,component_id):
    ''' Handle subcomponents for a specific component '''
    c=Component.objects.get(pk=component_id)
    existingsubs=c.components.all()
    allsubs=Component.objects.all()
    available=[]
    for s in allsubs:
        if s not in existingsubs: available.append(s)
    return render_to_response('componentSubs.html',
        {'c':c,'available':available,'existing':existingsubs})
        
def assignComponent(request,component_id,sub_id):
    ''' Assign a subcomponent id to a component '''
    url=reverse('cmip5q.protoq.views.componentSubs',args=(component_id,))
    try:
        c=Component.objects.get(pk=component_id)
        s=Component.objects.get(pk=sub_id)
    except:
        message="Unable to handle components %s and %s"%(component_id,sub_id)
        return render_to_response('error.html',{'message':message,'url':url})
    c.components.add(s)
    c.save()
    return HttpResponseRedirect(url)
   
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
    return render_to_response('reference.html',{'rform':rform,'url':url,'label':'add'})
        
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
    return render_to_response('reference.html',{'rform':rform,'url':url,'label':'update'})
    
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

def listSimulations(request,centre_id=None,experiment_id=None):
    return HttpResponse('Not Implemented')

def editSimulation(request,simulation_id):
    s=Simulation.objects.get(pk=simulation_id)
    e=s.experiment
    if request.method=='POST':
        simform=SimulationForm(request.POST,instance=s)
        if simform.is_valid():
            simform.save()
            return HttpResponseRedirect(
                    reverse('cmip5q.protoq.views.centre',args=(s.centre_id,)))
    else:
        simform=SimulationForm(instance=s)
    url='/cmip5/simulations/edit/%s/'%simulation_id
    return render_to_response('simulation.html',
        {'simform':simform,'url':url,'label':'Update','exp':e})

def addSimulation(request,centre_id,experiment_id):
    ''' Handle the addition of a new simulation '''
    
    # first see whether a model and platform have been created!
    # if not, we should return an error message ..
    c=Centre.objects.get(pk=centre_id)
    p=c.platform_set.values()
    m=c.component_set.values()
    e=Experiment.objects.get(pk=experiment_id)
    url=reverse('cmip5q.protoq.views.centre',args=(centre_id,))
    if len(p)==0:
        ''' Require them to create a platform '''
        message='You need to create a platform before creating a simulation'
        return render_to_response('error.html',{'message':message,'url':url})
    elif len(m)==0:
        ''' Require them to create a model'''
        message='You need to create a model before creating a simulation'
        return render_to_response('error.html',{'message':message,'url':url})
    
    if request.method=='POST':
        # we need to add the things that we know and didn't ask for via the
        # form ... 
        c=Centre.objects.get(pk=centre_id)
        u=str(uuid.uuid1())
        s=Simulation(centre=c,experiment=e,uri=u)
        simform=SimulationForm(request.POST,instance=s)
        if simform.is_valid():
            simform.save()
            return HttpResponseRedirect(reverse('cmip5q.protoq.views.centre',args=(centre_id,)))
    else:
        simform=SimulationForm()
    url='/cmip5/simulations/add/%s/%s/'%(centre_id,experiment_id)
    return render_to_response('simulation.html',
        {'simform':simform,'url':url,'label':'Add','exp':e})
         
##### PLATFORM HANDLING ###########################################################
# we can do this simply because p doesn't have any mandatory links.

def addPlatform(request,centre_id):
    ''' Add a new platform to a centre '''
    u=str(uuid.uuid1())
    p=Platform(centre=Centre.objects.get(pk=centre_id),uri=u)
    p.save()
    return HttpResponseRedirect(
        reverse('cmip5q.protoq.views.editPlatform',args=[p.id]))
        
def editPlatform(request,platform_id):
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
    return render_to_response('platform.html',
                {'pform':pform,'centre_id':p.centre_id,'platform_id':p.id})
        
########## EXPERIMENT VIEWS ##################
    
def viewExperiment(request,experiment_id):
    return render_to_response('experiment.html',{})
    
    
    