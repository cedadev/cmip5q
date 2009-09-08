# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.BaseView import *
from cmip5q.protoq.utilities import PropertyForm, tabs
from cmip5q.protoq.components import componentHandler
from cmip5q.protoq.simulations import simulationHandler
from cmip5q.protoq.references import referenceHandler
from cmip5q.protoq.coupling import couplingHandler
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
    newplatURL=reverse('cmip5q.protoq.views.platformEdit',args=(c.id,))
    viewsimURL=reverse('cmip5q.protoq.views.simulationList',args=(c.id,))
    
    
    logging.info('Viewing %s'%c.id)
    return render_to_response('centre.html',
        {'centre':c,'models':models,'platforms':platforms,
        'newmod':newmodURL,'newplat':newplatURL,'sims':sims,'viewsimurl':viewsimURL,
        'tabs':tabs(c.id,'Sum'),'notAjax':not request.is_ajax()})
      
#### COMPONENT HANDLING ###########################################################

# Provide a vew interface to the component object 
def componentAdd(request,centre_id):
    ''' Add a component '''
    c=componentHandler(centre_id)
    return c.edit(request)
    
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
  
def componentCup(request,centre_id,component_id):
    ''' Return couplings for a component '''
    c=couplingHandler(centre_id,request)
    return c.component(component_id)

def componentInp(request,centre_id,component_id):
    ''' Return inputs for a component '''
    c=componentHandler(centre_id,component_id)
    return c.inputs(request)

def componentNum(request,centre_id,component_id):
    ''' Return numerics of the component '''
    c=componentHandler(centre_id,component_id)
    return c.numerics()

def componentOut(request,centre_id,component_id):
   ''' return outputs of a component '''
   c=componentHandler(centre_id,component_id)
   return c.outputs()
   
###### REFERENCE HANDLING ######################################################
   
def referenceList(request,centre_id=None):
    ''' Handle the listing of references, including the options to edit, or add'''
    rH=referenceHandler(centre_id)
    return rH.list()

def referenceEdit(request,centre_id,reference_id=None):
    ''' Display or edit one reference '''
    rH=referenceHandler(centre_id)
    return rH.edit(request,reference_id,request.is_ajax())
    
def assignReferences(request,centre_id,resourceType,resource_id):
    ''' Make the link between a reference and a component '''
    rH=referenceHandler(centre_id)
    return rH.assign(request,resourceType,resource_id)
    
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

def conformanceMain(request,centre_id,simulation_id):
    s=simulationHandler(centre_id,simulation_id)
    return s.conformanceMain(request)

def simulationCup(request,centre_id,simulation_id,coupling_id=None,ctype=None):
    ''' Return couplings for a component '''
    c=couplingHandler(centre_id,request)
    if ctype:
        return c.resetClosures(simulation_id,coupling_id,ctype)
    else:
        return c.simulation(simulation_id)
   
#### CONFORMANCE HANDLING APPEARS IN THE SIMULATION FILE  ###########################################################
 
def conformanceEdit(request,cen_id,sim_id,req_id):
    s=simulationHandler(cen_id,simid=sim_id)
    return s.conformanceEdit(request,req_id)
            
##### PLATFORM HANDLING ###########################################################

class MyPlatformForm(PlatformForm):
    def __init__(self,*args,**kwargs):
        PlatformForm.__init__(self,*args,**kwargs)
        self.vocabs={'hardware':Vocab.objects.get(name='hardwareType'),
                     'processor':Vocab.objects.get(name='processorType'),
                     'interconnect':Vocab.objects.get(name='interconnectType')}
        for key in self.vocabs:
            self.fields[key].queryset=Value.objects.filter(vocab=self.vocabs[key])

def platformEdit(request,centre_id,platform_id=None):
    ''' Handle platform editing '''
    c=Centre.objects.get(id=centre_id)
    # start by getting a form ...
    if platform_id is None:
        editURL=reverse('cmip5q.protoq.views.platformEdit',args=(centre_id,))
        if request.method=='GET':
            pform=MyPlatformForm()
        elif request.method=='POST':
            pform=MyPlatformForm(request.POST)
        pname=''
        puri=str(uuid.uuid1())
    else:
        editURL=reverse('cmip5q.protoq.views.platformEdit',args=(centre_id,platform_id,))
        p=Platform.objects.get(pk=platform_id)
        puri=p.uri
        pname=p.abbrev
        if request.method=='GET':
            pform=MyPlatformForm(instance=p)
        elif request.method=='POST':
            pform=MyPlatformForm(request.POST,instance=p)
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
                {'pform':pform,'url':editURL,'c':c,'pname':pname,
                'tabs':tabs(centre_id,'Chooser')})
        
########## EXPERIMENT VIEWS ##################
    
def viewExperiment(request,experiment_id):
    e=Experiment.objects.get(pk=experiment_id)
    r=e.requirements.all()
    return render_to_response('experiment.html',{'e':e,'reqs':r,'notAjax':not request.is_ajax()})

######## HELP and ABOUT ###############

def help(request,cen_id):
    return render_to_response('help.html',{'tabs':tabs(cen_id,'Help')})
 
def about(request,cen_id):
    return render_to_response('about.html',{'tabs':tabs(cen_id,'About')})

############ DATA VIEWS ######################

def dataList(request,cen_id):
    do=DataObject.objects.all()
    for d in do:
        d.editURL=reverse('cmip5q.protoq.views.dataEdit',args=(cen_id,d.id))
    c=Centre.objects.get(pk=cen_id)
    c.url=reverse('cmip5q.protoq.views.centre',args=(cen_id,))
    surl=reverse('cmip5q.protoq.views.simulationList',args=(cen_id,))
    editurl=reverse('cmip5q.protoq.views.dataEdit',args=(cen_id,))
    return render_to_response('file_list.html',{'objects':do,'surl':surl,'c':c,
                                'tabs':tabs(cen_id,'Files'),
                                'form':DataObjectForm(),
                                'editURL':editurl,
                                'notAjax':not request.is_ajax()})
                                
def dataEdit(request,cen_id,object_id=None):
    
    ''' Handle the editing of a specific data object '''
    
    if object_id is None:
        editURL=reverse('cmip5q.protoq.views.dataEdit',args=(cen_id,))
        if request.method=='GET':
            # then we're starting afresh
            dform=DataObjectForm()
        elif request.method=='POST':
            dform=DataObjectForm(request.POST)
    else:
        editURL=reverse('cmip5q.protoq.views.dataEdit',args=(cen_id,object_id,))
        d=DataObject.objects.get(pk=object_id)
        if request.method=='GET':
            dform=DataObjectForm(instance=d)
        elif request.method=='POST':
            dform=DataObjectForm(request.POST,instance=d)
  
    if request.method=='POST':
        if dform.is_valid():
            d=dform.save()
            return HttpResponseRedirect(reverse('cmip5q.protoq.views.dataList',args=(cen_id,)))
    #FIXME: Should this be indented?
    else:
        editURL=reverse('cmip5q.protoq.views.dataEdit',args=(cen_id))
    return render_to_response('data.html',
            {'form':dform,'editURL':editURL,'tabs':tabs(cen_id,'FileEdit'),
            'notAjax':not request.is_ajax()})
            
############# Ensemble View ###############################            
            
def ensemble(request,cen_id,sim_id,ens_id=None):
    ''' Show the physical ensemble description page '''
    if ens_id is None:
        s=Simulation.objects.get(id=sim_id)
        e=PhysicalEnsemble.objects.filter(simulation=s)
        if len(e)==0:
            e=PhysicalEnsemble(ensembleDescription='Describe me',simulation=s)
            e.save()
        else: e=e[0]     
    else:
        e=PhysicalEnsemble.objects.get(id=ens_id)
        s=e.simulation
    
    
    urls={'self':reverse('cmip5q.protoq.views.ensemble',args=(cen_id,sim_id,)),
          'sim':reverse('cmip5q.protoq.views.simulationEdit',args=(cen_id,sim_id,)),
          'mods':reverse('cmip5q.protoq.views.assign',
                     args=(cen_id,'ensemble',e.id,'codemodification'))}
                     
    if request.method=='GET':
        eform=EnsembleForm({'description':e.ensembleDescription})
    elif request.method=='POST':
        eform=EnsembleForm(request.POST)
    if request.method=='POST':
        if eform.is_valid():
            d=eform.cleaned_data['description']
            e.ensembleDescription=d
            e.save()
            return HttpResponseRedirect(urls['self'])
    codeMods=e.codeModification.get_query_set()
    for c in codeMods:
        c.editURL=reverse('cmip5q.protoq.views.edit',args=(cen_id,'codemodification',c.id,'ensemble',e.id))
    return render_to_response('ensemble.html',
               {'s':s,'e':e,'urls':urls,'eform':eform,'codeMods':codeMods,
               'tabs':tabs(cen_id,'tmp')})
               
               
    
############ Simple Generic Views ########################

class ViewHandler(BaseViewHandler):
    ''' Specialises Base View for the various resource understood as a "simple"
    view '''
    #pattern: resource class, resourcetype, form
    SupportedResources={'initialcondition':[
                                InitialCondition,
                                'initialCondition',
                                InitialConditionForm],
                        'file':[
                                DataObject,
                                'file',
                                DataObjectForm],
                        'codemodification':[
                                CodeModification,
                                'codeModification',
                                CodeModificationForm]
                                }
    def __init__(self,cen_id,resourceType,obj_id,target_id,targetType):
        ''' We can have some combination of the above at initialiation time '''
        
        if resourceType not in self.SupportedResources:
            raise ValueError('Unknown resource type %s '%resourceType)
        
        constraints,targetURL,target=None,None,None
        if targetType is not None:
            try:
                target={'simulation':Simulation,
                        'ensemble':PhysicalEnsemble
                       }[targetType].objects.get(id=target_id)
            except Exception,e:
                return HttpResponse(str(e))
            targetURL={'simulation':reverse('cmip5q.protoq.views.simulationEdit',
                                            args=(cen_id,target_id,)),
                       'ensemble':reverse('cmip5q.protoq.views.ensemble',
                                           args=(cen_id,0,target_id,))
                      }[targetType]

        #We may need a constraint tuple to be used by specialisation methods 
        #if resourceType=='boundarycondition' and targetType=='simulation':
        #    # we need to constrain the boundary condition form to the right boundary conditions
        #    model=target.numericalModel
        #    constraints=(model,)
           
        SupportedResource=self.SupportedResources[resourceType]
        # The base view handler needs some or all of this:   
        data={'centre':cen_id,
              'resource':{'type':SupportedResource[1],'id':obj_id,
                           'class':SupportedResource[0]},
              'target':{'type':targetType,'id':target_id,'url':targetURL,'instance':target},
              'form':SupportedResource[2],
              'constraints':constraints}
              
        BaseViewHandler.__init__(self,data)

def edit(request,cen_id,returnType,resourceType,obj_id=None,target_id=None,targetType=None):
    ''' This is the generic simple view editor '''
    
    h=ViewHandler(cen_id,resourceType,obj_id,target_id,targetType)
    return h.edit(request,returnType)

def list(request,cen_id,resourceType,targetType=None,target_id=None):
    ''' This is the generic simple view lister '''
   
    h=ViewHandler(cen_id,resourceType,None,target_id,targetType)
    return h.list()

def assign(request,cen_id,targetType,target_id,resourceType):
    ''' Provide a page to allow the assignation of resources of type resourceType
    to resource target_id of type targetType '''
   
    h=ViewHandler(cen_id,resourceType,None,target_id,targetType)
    return h.assign(request) 
    
    

