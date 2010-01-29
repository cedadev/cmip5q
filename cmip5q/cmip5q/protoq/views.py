# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.forms import *

from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.BaseView import *
from cmip5q.protoq.utilities import  tabs, sublist
from cmip5q.protoq.components import componentHandler
from cmip5q.protoq.simulations import simulationHandler
from cmip5q.protoq.cimHandler import cimHandler
from cmip5q.protoq.XML import *
from cmip5q.protoq.utilities import render_badrequest, gracefulNotFound

#from cmip5q.protoq.references import referenceHandler
from cmip5q.protoq.coupling import couplingHandler
from django import forms
import uuid
import logging
import simplejson

MESSAGE=''

def completionHelper(request,vocabName):
    ''' This method provides support for ajax autocompletion within a specific vocabulary '''
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'q'):
            value = request.GET[u'q']
            # Ignore queries shorter than length 3
            if len(value) > 2:
                try:
                    v=Vocab.objects.get(name=vocabName)
                except: return HttpResponseBadRequest('Invalid vocab %s'%vocabName)
                model_results = Value.objects.filter(vocab=v).filter(value__startswith=value)
                results = [ (x.__unicode__(), x.id) for x in model_results ]
   
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')
    return HttpResponse

def genericDoc(request,cid,docType,pkid,method):
    ''' Handle the generic documents '''
    try:
        klass={'simulation':Simulation,'experiment':Experiment,'component':Component,
           'platform:':Platform}[docType]
    except:
        return render_badrequest('error.html',{'message:':'Document type %s not known'%docType})
    try:
        obj=klass.objects.get(id=pkid)
    except:
        return render_badrequest('error.html',{'message':'Document id %s not known as %s'%(pkid,docType)})
    c=cimHandler(obj)
    try:
        cmethod=getattr(c,method)
    except:
        return render_badrequest('error.html',{'message':'Method %s not known as a generic document handler'%method})
    return cmethod()

def persistedDoc(request,docType,uri,version=0):
    ''' persisted document handling'''
    if docType not in ('platform','experiment','simulation','component'):
            return HttpResponseBadRequest('Invalid document type requests - %s'%docType)
    set=CIMObject.objects.filter(uri=uri)
    if len(set)==0:
        return render_badrequest('error.html',{'message':'Document with uri - %s - not found'%uri})
    if version<>0:
        try:
            set=set.filter(documentVersion=version)
            if len(set)<>1: 
                logging.info('CIM Document Inconsistency - %s identical versions'%len(set))
            obj=set.get(documentVersion=version)
        except:
            logging.info('Attempt to retrieve %s with version %s failed'%(uri,version))
            return render_badrequest('error.html',{'message':'Document with uri - %s - has no version %s'%(uri,version)})
    else:
        obj=set[len(set)-1]
    return HttpResponse(obj.xmlfile.read(),mimetype='application/xml')

def index(request):
    #find all the centre objects
    centre_list=Centre.objects.all()
    f=CentreForm() 
    return render_to_response('default.html',{'centre_list':centre_list,'cf':f})
   
def centres(request):
    ''' For choosing amongst centres '''
    p=Centre.objects.all()
    p=p.exclude(abbrev='CMIP5')
    if request.method=='POST':
        #yep we've selected something
        try:
            selected_centre=p.get(id=request.POST['choice'])
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
    c=Centre.objects.get(id=centre_id)
    models=[]
    models=[Component.objects.get(id=m.id) for m in c.component_set.filter(scienceType='model')]
    #monkey patch the urls to edit these ...
    for m in models:
        m.url=reverse('cmip5q.protoq.views.componentEdit',args=(c.id,m.id))
        m.cpURL=reverse('cmip5q.protoq.views.componentCopy',args=(c.id,m.id))
    platforms=[Platform.objects.get(id=p['id']) for p in c.platform_set.values()]
    for p in platforms:
        p.url=reverse('cmip5q.protoq.views.platformEdit',args=(c.id,p.id))
    sims=Simulation.objects.filter(centre=c.id)
    for s in sims:
        s.url=reverse('cmip5q.protoq.views.simulationEdit',args=(c.id,s.id))
    
    newmodURL=reverse('cmip5q.protoq.views.componentAdd',args=(c.id,))
    newplatURL=reverse('cmip5q.protoq.views.platformEdit',args=(c.id,))
    viewsimURL=reverse('cmip5q.protoq.views.simulationList',args=(c.id,))
    
    refs=Reference.objects.filter(centre=c)
    files=DataContainer.objects.filter(centre=c)
    parties=ResponsibleParty.objects.filter(centre=c)
    
    logging.info('Viewing %s'%c.id)
    return render_to_response('centre.html',
        {'centre':c,'models':models,'platforms':platforms,
         'refs':refs,'files':files,'parties':parties,
        'newmod':newmodURL,'newplat':newplatURL,'sims':sublist(sims,3),'viewsimurl':viewsimURL,
        'tabs':tabs(request,c.id,'Summary'),'notAjax':not request.is_ajax()})
      
#### COMPONENT HANDLING ###########################################################

# Provide a vew interface to the component object 
def componentAdd(request,centre_id):
    ''' Add a component '''
    c=componentHandler(centre_id)
    return c.edit(request)

@gracefulNotFound
def componentEdit(request,centre_id,component_id):
    ''' Edit a component '''
    c=componentHandler(centre_id,component_id)
    return c.edit(request)
    
@gracefulNotFound   
def componentSub(request,centre_id,component_id):
    ''' Add a subcomponent onto a component '''
    c=componentHandler(centre_id,component_id)
    return c.addsub(request)
    
@gracefulNotFound
def componentRefs(request,centre_id,component_id):
    ''' Manage the references associated with a component '''
    c=componentHandler(centre_id,component_id)
    return c.manageRefs(request)
    
@gracefulNotFound
def componentTxt(request,centre_id,component_id):
    ''' Return a textual view of the component with possible values '''
    c=componentHandler(centre_id,component_id)
    return c.XMLasText()
  
@gracefulNotFound
def componentCup(request,centre_id,component_id):
    ''' Return couplings for a component '''
    c=couplingHandler(centre_id,request)
    return c.component(component_id)

@gracefulNotFound
def componentInp(request,centre_id,component_id):
    ''' Return inputs for a component '''
    c=componentHandler(centre_id,component_id)
    return c.inputs(request)

@gracefulNotFound
def componentCopy(request,centre_id,component_id):
   c=componentHandler(centre_id,component_id)
   return c.copy(request)
   
###### REFERENCE HANDLING ######################################################
#   
#def referenceList(request,centre_id=None):
#    ''' Handle the listing of references, including the options to edit, or add'''
#    rH=referenceHandler(centre_id)
#    return rH.list()
#
#def referenceEdit(request,centre_id,reference_id=None):
#    ''' Display or edit one reference '''
#    rH=referenceHandler(centre_id)
#    return rH.edit(request,reference_id,request.is_ajax())
#    
#def assignReferences(request,centre_id,resourceType,resource_id):
#    ''' Make the link between a reference and a component '''
#    rH=referenceHandler(centre_id)
#    return rH.assign(request,resourceType,resource_id)
#    
###### SIMULATION HANDLING ######################################################

@gracefulNotFound
def simulationEdit(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simid=simulation_id)
    return s.edit(request)

def simulationAdd(request,centre_id,experiment_id):
    s=simulationHandler(centre_id,expid=experiment_id)
    return s.add(request)

def simulationList(request,centre_id):
    s=simulationHandler(centre_id)
    return s.list(request)

@gracefulNotFound
def simulationCopy(request,centre_id):
    s=simulationHandler(centre_id)
    return s.copy(request)

@gracefulNotFound
def conformanceMain(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simulation_id)
    return s.conformanceMain(request)

@gracefulNotFound
def simulationCup(request,centre_id,simulation_id,coupling_id=None,ctype=None):
    ''' Return couplings for a component '''
    c=couplingHandler(centre_id,request)
    if ctype: # this method deprecated.
        return c.resetClosures(simulation_id,coupling_id,ctype)
    else:
        return c.simulation(simulation_id)
    
def simulationCupReset(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simulation_id)
    return s.resetCouplings()
   
#### CONFORMANCE HANDLING APPEARS IN THE SIMULATION FILE  ###########################################################
 
@gracefulNotFound
def conformanceEdit(request,cen_id,sim_id,req_id):
    s=simulationHandler(cen_id,simid=sim_id)
    return s.conformanceEdit(request,req_id)
            
##### PLATFORM HANDLING ###########################################################

class MyPlatformForm(PlatformForm):
    def __init__(self,centre,*args,**kwargs):
        PlatformForm.__init__(self,*args,**kwargs)
        self.vocabs={'hardware':Vocab.objects.get(name='hardwareType'),
                     'vendor':Vocab.objects.get(name='vendorType'),
                     'compiler':Vocab.objects.get(name='compilerType'),
                     'operatingSystem':Vocab.objects.get(name='operatingSystemType'),
                     'processor':Vocab.objects.get(name='processorType'),
                     'interconnect':Vocab.objects.get(name='interconnectType')}
        for key in self.vocabs:
            self.fields[key].queryset=Value.objects.filter(vocab=self.vocabs[key])
        qs=ResponsibleParty.objects.filter(centre=centre)|ResponsibleParty.objects.filter(party=centre)
        self.fields['funder'].queryset=qs
        self.fields['contact'].queryset=qs
        
@gracefulNotFound
def platformEdit(request,centre_id,platform_id=None):
    ''' Handle platform editing '''
    c=Centre.objects.get(id=centre_id)
    # start by getting a form ...
    if platform_id is None:
        editURL=reverse('cmip5q.protoq.views.platformEdit',args=(centre_id,))
        if request.method=='GET':
            pform=MyPlatformForm(c)
        elif request.method=='POST':
            pform=MyPlatformForm(c,request.POST)
        p=None
        puri=str(uuid.uuid1())
    else:
        editURL=reverse('cmip5q.protoq.views.platformEdit',args=(centre_id,platform_id,))
        p=Platform.objects.get(id=platform_id)
        puri=p.uri
        if request.method=='GET':
            pform=MyPlatformForm(c,instance=p)
        elif request.method=='POST':
            pform=MyPlatformForm(c,request.POST,instance=p)
    # now we've got a form, handle it        
    if request.method=='POST':
        if pform.is_valid():
            p=pform.save(commit=False)
            p.centre=c
            p.uri=puri
            p.save()
            return HttpResponseRedirect(
                reverse('cmip5q.protoq.views.centre',args=(centre_id,)))
    
    return render_to_response('platform.html',
                {'pform':pform,'url':editURL,'p':p,'c':c,'esgready':1,'cform':pform,
                'tabs':tabs(request,centre_id,'Platform')})
                # point cform at pform too so that the completion html can use a common variable.
        
########## EXPERIMENT VIEWS ##################
    
def viewExperiment(request,cen_id,experiment_id):
    e=Experiment.objects.get(id=experiment_id)
    r=e.requirements.all()
    return render_to_response('experiment.html',{'e':e,'reqs':r,'tabs':tabs(request,cen_id,'Experiment')})

######## HELP and ABOUT ###############

def help(request,cen_id):
    return render_to_response('help.html',{'tabs':tabs(request,cen_id,'Help')})
 
def about(request,cen_id):
    return render_to_response('about.html',{'tabs':tabs(request,cen_id,'About')})

def intro(request,cen_id):
    return render_to_response('intro.html',{'tabs':tabs(request,cen_id,'Intro')})
            
############# Ensemble View ###############################            
            
def ensemble(request,cen_id,sim_id):
    ''' Manage ensembles for a given simulation '''
    s=Simulation.objects.get(id=sim_id)
    e=Ensemble.objects.get(simulation=s)
    e.updateMembers()  # in case members were deleted via their code mods or ics.
    members=e.ensemblemember_set.all()
        
    EnsembleMemberFormset=modelformset_factory(EnsembleMember,form=EnsembleMemberForm,extra=0,exclude=('ensemble','memberNumber'))
    
    urls={'self':reverse('cmip5q.protoq.views.ensemble',args=(cen_id,sim_id,)),
          'sim':reverse('cmip5q.protoq.views.simulationEdit',args=(cen_id,sim_id,)),
          'mods':reverse('cmip5q.protoq.views.list',
                     args=(cen_id,'modelmod','ensemble',s.id,)),
          'ics':reverse('cmip5q.protoq.views.list',
                     args=(cen_id,'inputmod','ensemble',s.id,)),        
                     }                 
    if request.method=='GET':
        eform=EnsembleForm(instance=e,prefix='set')
        eformset=EnsembleMemberFormset(queryset=members,prefix='members')
    elif request.method=='POST':
        if e.etype is not None:
            eformset=EnsembleMemberFormset(request.POST,queryset=members,prefix='members')
        else: eformset=None
        eform=EnsembleForm(request.POST,instance=e,prefix='set')
        ok=True
        if eform.is_valid():
            eform.save()
        else: ok=False
        if eformset is not None:
            if eformset.is_valid():
                eformset.save()
            else: ok=False
        logging.debug('POST to ensemble is ok - %s'%ok)
        if ok: return HttpResponseRedirect(urls['self'])
    return render_to_response('ensemble.html',
               {'s':s,'e':e,'urls':urls,'eform':eform,'eformset':eformset,
               'tabs':tabs(request,cen_id,'Ensemble')})
               
               
    
############ Simple Generic Views ########################

class ViewHandler(BaseViewHandler):
    ''' Specialises Base View for the various resource understood as a "simple"
    view '''
    
    # The base view handler needs a mapping between the resource type
    # as it will appear in a URL, the name it is used when an attribute, 
    # the resource class and the resource class form
    # (so keys need to be lower case)
    SupportedResources={'modelmod':{'attname':'modelMod',
                            'title':'Model Modifications','tab':'ModelMods',
                             'class':ModelMod,'form':ModelModForm},
                        'inputmod':{'attname':'inputMod',
                            'title':'Input Modifications','tab':'InputMods',
                             'class':InputMod,'form':InputModForm}, 
                        'file':{'attname':'dataContainer',
                            'title':'Files and Variables','tab':'Files & Vars',
                            'class':DataContainer,'form':DataHandlingForm},
                        'reference':{'attname':'references',
                            'title':'References','tab':'References',
                            'class':Reference,'form':ReferenceForm},
                        'parties':{'attname':'responsibleParty',
                                   'title':'Parties','tab':'Parties',
                                   'class':ResponsibleParty,'form':ResponsiblePartyForm},
                        }
    # Note that we don't expect to be able to assign files, since we'll directly
    # attach objects within files as appropriate.
                        
    # Some resources are associated with specific targets, so we need a mapping
    # between how they appear in URLs and the associated django classes
    # (so keys need to be lower case)                    
                        
    SupportedTargets={'simulation':{'class':Simulation,'attname':'simulation'},
                      'centre':{'class':Centre,'attname':'centre'},
                      'component':{'class':Component,'attname':'component'},
                      'ensemble':{'class':Simulation,'attname':'simulation'},
                     }
                     
    # and for each of those we need to get back to the target view/edit, and for
    # that we need the right function name
    
    SupportedTargetReverseFunctions={
                      'simulation':'cmip5q.protoq.views.simulationEdit',
                      'centre':'cmip5q.protoq.views.centre',
                      'component':'cmip5q.protoq.views.componentEdit',
                      'ensemble':'cmip5q.protoq.views.ensemble',
                      }
                        
    # Now the expected usage of this handler is for
    # codemodifications associated with a given model (assign to a simulation and list)
    # references for a given component (assign to a component and list)
    # data objects in general (list)
    # initial conditions (assign to a simulation) and list
                        
    def __init__(self,cen_id,resourceType,resource_id,target_id,targetType):
        ''' We can have some combination of the above at initialiation time '''
        
        if resourceType not in self.SupportedResources:
            raise ValueError('Unknown resource type %s '%resourceType)
     
        if targetType is not None:
            # We grab an instance of the target
            if targetType not in self.SupportedTargets:
                raise ValueError('Unknown target type %s'%targetType)
            try:
                target=self.SupportedTargets[targetType]
                target['type']=targetType
                target['instance']=target['class'].objects.get(id=target_id)
            except Exception,e:
                # FIXME: Handle this more gracefully
                raise ValueError('Unable to find resource %s with id %s'%(targetType,target_id))
            # and work out what the url will be to return to this target instance
            target['url']=reverse(self.SupportedTargetReverseFunctions[targetType],
                                  args=[cen_id,target_id])
        else: target=None 
        
        resource=self.SupportedResources[resourceType]
        resource['type']=resourceType
        resource['id']=resource_id
     
        BaseViewHandler.__init__(self,cen_id,resource,target)
        
    def objects(self):
        ''' Returns a list of objects to display, as a function of the resource and target types'''
        objects=self.resource['class'].objects.all()
        if self.resource['type']=='modelmod' and self.target['type']=='simulation':
            # for code modifications, we need to get those associated with a model for a simulation
            constraintSet=Component.objects.filter(model=self.target['instance'].numericalModel)
            objects=objects.filter(component__in=constraintSet)
        if self.resource['type'] in ['reference','file']:
            #objects=objects.filter(centre__in=[None,self.centre]) doesn't work
            objects=objects.filter(centre=None)|objects.filter(centre=self.centre)
            objects=objects.order_by('name')
        elif self.resource['type']=='modelmod':
            objects=objects.filter(centre=self.centre)
            objects=objects.order_by('mnemonic')
        elif self.resource['type']=='parties':
            objects=objects.filter(centre=self.centre).order_by('name')
        elif self.resource['type']=='inputmod':
            objects=objects.filter(centre=self.centre)
            objects=objects.order_by('mnemonic')
        return objects
        
    def constraints(self):
        ''' Return constraints for form specialisation '''
        if self.resource['type']=='modelmod':
            if self.target['type']=='simulation':
                return self.target['instance'].numericalModel
            elif self.target['type']=='component':
                return self.target['instance']
            elif self.target['type']=='ensemble':
                return self.target['instance'].numericalModel
        if self.resource['type'] in ['reference','file']:
            return self.centre 
        if self.resource['type']=='inputmod':
            if self.target['type']=='ensemble':
                return self.target['instance'] # which should be a simulation
                   
        return None

def edit(request,cen_id,resourceType,resource_id,targetType=None,target_id=None,returnType=None):
    ''' This is the generic simple view editor '''
    h=ViewHandler(cen_id,resourceType,resource_id,target_id,targetType)
    return h.edit(request,returnType)

def delete(request,cen_id,resourceType,resource_id,targetType=None,target_id=None,returnType=None):
    ''' This is the generic simple item deleter '''
    h=ViewHandler(cen_id,resourceType,resource_id,target_id,targetType)
    return h.delete(request,returnType)

def list(request,cen_id,resourceType,targetType=None,target_id=None):
    ''' This is the generic simple view lister '''

    h=ViewHandler(cen_id,resourceType,None,target_id,targetType)
    return h.list(request)

def assign(request,cen_id,resourceType,targetType,target_id):
    ''' Provide a page to allow the assignation of resources of type resourceType
    to resource target_id of type targetType '''
    if resourceType=='file':
        return render_badrequest('error.html',{'message':'Cannot assign files to targets, assign objects from within them!'})
   
    h=ViewHandler(cen_id,resourceType,None,target_id,targetType)
    return h.assign(request) 
    
