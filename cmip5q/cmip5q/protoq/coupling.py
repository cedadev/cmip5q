from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django import forms

from cmip5q.protoq.models import *


CouplingFormSet=modelformset_factory(Coupling,extra=0,exclude=('component','targetInput'))
InternalClosureFormSet=modelformset_factory(InternalClosure,can_delete=True,
                                    form=InternalClosureForm,
                                    exclude=('coupling'))
ExternalClosureFormSet=modelformset_factory(ExternalClosure,can_delete=True,
                                    form=ExternalClosureForm,
                                    exclude=('coupling'))                                

#https://www.cduce.org/~abate/index.php?q=dynamic-forms-with-django

class MyInternalClosures(InternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ic%s'%q
        self.coupling=q
        qset=InternalClosure.objects.filter(coupling=q)
        InternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)
    def save(self):
        instances=InternalClosureFormSet.save(self,commit=False)
        print 'saving internal closures for %s'%self.coupling
        for i in instances:
            i.coupling=self.coupling
            i.save()
    
class MyExternalClosures(ExternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ec%s'%q
        self.coupling=q
        qset=ExternalClosure.objects.filter(coupling=q)
        ExternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)
    def save(self):
        instances=ExternalClosureFormSet.save(self,commit=False)
        print 'saving external closures for %s'%self.coupling
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
    
    def __init__(self,component,data=None,simulation=None):
        ''' Initialise the forms needed to interact for a (model) component '''
        
        self.component=component
        self.simulation=simulation
        
        self.model=self.component.model
        self.queryset=Coupling.objects.filter(component=self.component)
       
        # setup our vocabularies
        couplingType=Value.objects.filter(vocab=Vocab.objects.get(name='couplingType'))
        couplingFreqUnits=Value.objects.filter(vocab=Vocab.objects.get(name='FreqUnits'))
        spatialRegridding=Value.objects.filter(vocab=Vocab.objects.get(name='SpatialRegridding'))
        temporalRegridding=Value.objects.filter(vocab=Vocab.objects.get(name='TemporalRegridding'))
        
        self.couplingVocabs={'couplingType':couplingType,
                'couplingFreqUnits':couplingFreqUnits}
        self.closureVocabs={'spatialRegridding':spatialRegridding,
                'temporalRegridding':temporalRegridding}
                
        # Haven't worked out how to do this directly to forms in formsets, and this is commont to both
        # anyway
        self.widgets={'inputDescription':forms.Textarea({'cols':"100",'rows':"2"})}
        
        # rather than use a django formset for the couplings, we'll do them by
        # hand, but do the closures using a formset ...
        
        self.forms=[]
        # this is the list of relevant realm level components:
        BaseInternalQueryset=Component.objects.filter(model=self.model).filter(isRealm=True)
        for q in self.queryset:
            cf=CouplingForm(data,instance=q,prefix=q)
            title='Coupling into: %s'%q.targetInput
            for key in self.couplingVocabs:
                cf.fields[key].queryset=self.couplingVocabs[key]
            ic=MyInternalClosures(q,data)
            ec=MyExternalClosures(q,data)
            #make sure we don't offer up the target input owner component:
            iqs=BaseInternalQueryset.exclude(id__exact=q.targetInput.owner.id)
            self.forms.append(MyCouplingForm({'title':title,'cf':cf,'ic':ic,'ec':ec,'iqs':iqs}))
            
            
    def is_valid(self):
        ok=True
        for f in self.forms:
            r=f.cf.is_valid()
            if not r: ok=False
            r=f.ec.is_valid()
            if not r: ok=False
            r=f.ic.is_valid()
            if not r: ok=False
        return ok
            
    def specialise(self):
        for f in self.forms:
            for i in f.ic.forms+f.ec.forms:
                print i.fields.keys()
                #i.fields['inputDescription']=self.widgets['inputDescription']
                for key in self.closureVocabs:
                    i.fields[key].queryset=self.closureVocabs[key]
            
            for i in f.ic.forms:
                i.fields['target'].queryset=f.iqs
                    
    
    def save(self):
        for f in self.forms:
            # first the coupling form
            cf=f.cf.save(commit=False)
            cf.component=self.component
            cf.targetInput=self.queryset.get(id=cf.id).targetInput
            if self.simulation: cf.simulation=self.simulation
            cf.save()
            # now the external closures formset ...
            instances=f.ec.save()
            instances=f.ic.save()
            

            
