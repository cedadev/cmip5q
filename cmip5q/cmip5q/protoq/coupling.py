from django.conf import settings

from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django import forms

from cmip5q.protoq.models import *
from cmip5q.protoq.forms import *

from cmip5q.protoq.layoutUtilities import tabs

logging=settings.LOG

InternalClosureFormSet=modelformset_factory(InternalClosure,can_delete=True,
                                    form=InternalClosureForm,
                                    exclude=('coupling'))
ExternalClosureFormSet=modelformset_factory(ExternalClosure,can_delete=True,
                                    form=ExternalClosureForm,
                                    exclude=('coupling'))                                

#https://www.cduce.org/~abate/index.php?q=dynamic-forms-with-django


class ClosureReset:
    '''It's possible that when we show the simulation couplings that there have been new 
    closures created in the component interface, which haven't been replicated to the 
    simulation copy of the couplings. We will need to provide a button to reset closures 
    from the model copy. (It needs to be optional).'''
    def __init__(self,centre_id,simulation_id,coupling,ctype='None'):
        self.coupling=coupling
        self.closureModel={'ic':InternalClosure,'ec':ExternalClosure,'None':None}[ctype]
        args=[centre_id,simulation_id,coupling.id,]
        if ctype<>'None':args.append(ctype)
        self.url=reverse('cmip5q.protoq.views.simulationCup',args=args)
        self.returnURL=reverse('cmip5q.protoq.views.simulationCup',
                 args=(centre_id,simulation_id,))
    def reset(self):
        ''' Reset internal or external closures '''
        o=self.coupling.original
        set=self.closureModel.objects.filter(coupling=o)
        for i in set:
            i.makeNewCopy(self.coupling)
        return HttpResponseRedirect(self.returnURL)

class MyInternalClosures(InternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ic%s'%q
        self.coupling=q
        qset=InternalClosure.objects.filter(coupling=q)
        InternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)    
    def save(self):
        instances=InternalClosureFormSet.save(self,commit=False)
        logging.debug('saving internal closures for %s'%self.coupling)
        for i in instances:
            i.coupling=self.coupling
            i.save()
    
class MyExternalClosures(ExternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ec%s'%q
        self.coupling=q
        qset=ExternalClosure.objects.filter(coupling=q)
        ExternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)
        for i in self.forms:
            i.specialise()
    def save(self):
        instances=ExternalClosureFormSet.save(self,commit=False)
        logging.debug('saving external closures for %s'%self.coupling)
        for i in instances:
            i.coupling=self.coupling
            i.save()
            
class MyCouplingForm(object):
    def __init__(self,dict):
        for k in dict:
            self.__setattr__(k,dict[k])
    def __str__(self):
        s=self.title+str(self.cf)+str(self.ec)+str(self.ic)
        return s 

class MyCouplingFormSet:
    
    ''' Unlike a regular django formset, this one has to handle the closures within each 
    coupling instance, and we can do that using formsets, but not the couplings themselves '''
     #http://docs.djangoproject.com/en/dev/topics/forms/modelforms/#id1
    
    def __init__(self,model,simulation,queryset,data=None):
        ''' Initialise the forms needed to interact for a (model) component (indicated by the coupling group).'''
        
        self.model=model
        self.simulation=simulation
         
        # build up a queryset, chunked into the various types of component inputs
        ctypes=Term.objects.filter(vocab=Vocab.objects.get(name='InputTypes'))
        bcvalue=ctypes.get(name='BoundaryCondition')  #used for layout on coupling form
        afvalue=ctypes.get(name='AncillaryFile') #used for layout on closure form
        icvalue=ctypes.get(name='InitialCondition') # used for layout on closure form

        # setup our vocabularies
        inputTechnique=Term.objects.filter(vocab=Vocab.objects.get(name='InputTechnique'))
        FreqUnits=Term.objects.filter(vocab=Vocab.objects.get(name='FreqUnits'))
        
        # for closures
        spatialRegrid=Term.objects.filter(vocab=Vocab.objects.get(name='SpatialRegrid'))
        temporalTransform=Term.objects.filter(vocab=Vocab.objects.get(name='TimeTransformation'))
        
        self.couplingVocabs={ 'inputTechnique':inputTechnique,
                'FreqUnits':FreqUnits}
        self.closureVocabs={'spatialRegrid':spatialRegrid,
                'temporalTransform':temporalTransform}
               
        # rather than use a django formset for the couplings, we'll do them by
        # hand, but do the closures using a formset ... this made sense when
        # we had lots of closures, but less now ...
        
        self.forms=[]
        # this is the list of relevant realm level components:
        BaseInternalQueryset=Component.objects.filter(model=self.model).filter(isRealm=True)
        for q in queryset:
            cf=CouplingForm(data,instance=q,prefix=q)
            if self.simulation:
                centre_id=self.model.centre.id
                cf.icreset=ClosureReset(centre_id,simulation.id,q,'ic')
                cf.ecreset=ClosureReset(centre_id,simulation.id,q,'ec')
            title='Binding for %s %s'%(q.targetInput.ctype,q.targetInput)
            if self.simulation: title+=' for simulation %s'%self.simulation
            for key in self.couplingVocabs:
                cf.fields[key].queryset=self.couplingVocabs[key]
            ic=MyInternalClosures(q,data)
            ec=MyExternalClosures(q,data)
            #make sure we don't offer up the target input owner component:
            iqs=BaseInternalQueryset.exclude(id__exact=q.targetInput.owner.id)
            self.forms.append(MyCouplingForm({'title':title,
                                              'cf':cf,'ic':ic,'ec':ec,'iqs':iqs,
                                              'bcv':bcvalue,'afv':afvalue,'icv':icvalue}))
            
            
    def is_valid(self):
        ok=True
        for f in self.forms:
            r1=f.cf.is_valid()
            if not r1: ok=False
            r2=f.ec.is_valid()
            if not r2: ok=False
            r3=f.ic.is_valid()
            if not r3: ok=False
            print '[#',f.cf.errors,'##',f.ec.errors,'##',f.ic.errors,'#]'
        self.FormError=not ok   # used in coupling.html
        return ok
            
    def specialise(self):
        for f in self.forms:
            for i in f.ic.forms+f.ec.forms:
                #print i.fields.keys()
                #i.fields['inputDescription']=self.widgets['inputDescription']
                for key in self.closureVocabs:
                    i.fields[key].queryset=self.closureVocabs[key]
            for i in f.ic.forms:
                i.fields['target'].queryset=f.iqs
    def save(self):
        for f in self.forms:
            # first the coupling form
            cf=f.cf.save(commit=False)
            #cf.parent=self.parent
            #cf.targetInput=self.queryset.get(id=cf.id).targetInput
            cf.save()
            # now the external closures formset ...
            instances=f.ec.save()
            instances=f.ic.save()
            
class couplingHandler:
    ''' Handles couplings for models and simuations '''
    def __init__(self,centre_id,request):
        self.request=request
        self.method=request.method
        self.centre_id=centre_id
    def component(self,component_id):
        ''' Handle's model couplings '''
        self.component=Component.objects.get(id=component_id)
        # we do the couplings for the parent model of a component
        self.urls={'ok':reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,component_id,)),
              'return':reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,component_id,)),
              'returnName':'component'
              }
        return self.__handle()
    def simulation(self,simulation_id):
        simulation=Simulation.objects.get(id=simulation_id)
        self.component=simulation.numericalModel
        self.urls={'ok':reverse('cmip5q.protoq.views.simulationCup',args=(self.centre_id,simulation_id,)),
              'return':reverse('cmip5q.protoq.views.simulationEdit',args=(self.centre_id,simulation_id,)),
              'returnName':'simulation',
              'reset':reverse('cmip5q.protoq.views.simulationCupReset',args=(self.centre_id,simulation_id,)),
              }
        return self.__handle(simulation)
    def __handle(self,simulation=None):
        model=self.component.model
        assert (model != None,'Component %s has no model'%self.component)
        queryset=model.couplings(simulation)
        self.urls['model']=reverse('cmip5q.protoq.views.componentEdit',
                    args=(self.centre_id,model.id,))
        logging.debug('Handling %s coupling request for %s (simulation %s)'%(self.method,model,simulation))
       
        if self.method=='POST':
            Intform=MyCouplingFormSet(model,simulation,queryset,self.request.POST)
            if Intform.is_valid():
                Intform.save()
                return HttpResponseRedirect(self.urls['ok'])
            else:
                Intform.specialise()
        elif self.method=='GET':
            Intform=MyCouplingFormSet(model,simulation,queryset)
            Intform.specialise()
        labelstr='Coupling for %s'%model
        if simulation: labelstr+=' (in %s)'%simulation
        return render_to_response('coupling.html',{'c':model,'s':simulation,'urls':self.urls,
        'Intform':Intform,
        'tabs':tabs(self.request,self.centre_id,labelstr)})
        
    def resetClosures(self,simulation_id,coupling_id,ctype):
        logging.info('Deprecated reset closure method used for %s'%ctype)
        coupling=Coupling.objects.get(id=coupling_id)
        reset=ClosureReset(self.centre_id,simulation_id,coupling,ctype)
        return reset.reset()
    
    def update(self,coupling_id):
        ''' Used to update just one coupling, probably as an ajax activity '''
        pass
            
        
        
    
        
            
