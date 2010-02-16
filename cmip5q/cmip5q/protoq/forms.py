from django import forms
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from cmip5q.protoq.dropdown import DropDownWidget, DropDownSingleWidget

from cmip5q.protoq.models import *
from cmip5q.protoq.utilities import atomuri

from cmip5q.protoq.modelUtilities import uniqueness, refLinkField
from cmip5q.protoq.autocomplete import AutocompleteWidget, TermAutocompleteField

class ConformanceForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"3"}),required=False) 
    # We need the queryset, note that the queryset is limited in the specialisation
    q1,q2,q3=ModelMod.objects.all(),Coupling.objects.all(),Term.objects.all()
    mod=forms.ModelMultipleChoiceField(required=False,queryset=q1,widget=DropDownWidget(attrs={'size':'3'}))
    coupling=forms.ModelMultipleChoiceField(required=False,queryset=q2,widget=DropDownWidget(attrs={'size':'3'}))
    ctype=forms.ModelChoiceField(required=False,queryset=q3,widget=DropDownSingleWidget)
    class Meta:
        model=Conformance
        exclude=('simulation') # we know it
    def specialise(self,simulation):
        #http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        #relevant_components=Component.objects.filter(model=simulation.model)
        self.fields['mod'].queryset=simulation.modelMod.all()
        groups=CouplingGroup.objects.filter(simulation=simulation)  # we only expect one
        #it's possible we might end up trying to add conformances with no inputs ....
        if len(groups)<>0:
            assert (len(groups)==1, 'Simulation %s should have one or no coupling groups'%simulation)
            self.fields['coupling'].queryset=Coupling.objects.filter(parent=groups[0])
        else:
            self.fields['coupling'].queryset=[]
        v=Vocab.objects.get(name='ConformanceTypes')
        self.fields['ctype'].queryset=Term.objects.filter(vocab=v)
        self.showMod=len(self.fields['mod'].queryset)
        self.showCoupling=len(self.fields['coupling'].queryset)

class CouplingForm(forms.ModelForm):
    manipulation=forms.CharField(widget=forms.Textarea({'cols':'120','rows':'2'}),required=False)
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        for k in ('parent', 'targetInput','original'):
            self.fields[k].widget=forms.HiddenInput()
    class Meta:
        model=Coupling
        
class InternalClosureForm(forms.ModelForm):
     class Meta:
         model=InternalClosure
     def specialise(self):
         pass

class ExternalClosureForm(forms.ModelForm):
     class Meta:
         model=ExternalClosure
     def specialise(self):
         if self.instance.targetFile:
            self.fields['target'].queryset=DataObject.objects.filter(container=self.instance.targetFile)
                        


class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'class':'inputH1'}))
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    geneology=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=True)
   
    implemented=forms.BooleanField(required=False)
    yearReleased=forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'}),required=False)
    otherVersion=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}),required=False)
    
    controlled=forms.BooleanField(widget=forms.HiddenInput,required=False)
    class Meta:
        model=Component
        exclude=('centre','uri','model','realm','isRealm','isModel','visited',
                 'references','components')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        #concatenate to allow the centre to be shown as well as the other parties tied to it.
        qs=ResponsibleParty.objects.filter(centre=self.instance.centre)|ResponsibleParty.objects.filter(party=self.instance.centre)
        for i in ['author','contact','funder']: self.fields[i].queryset=qs
        if self.instance.controlled: 
            # We don't want this to be editable 
            self.fields['scienceType'].widget=forms.HiddenInput()
            self.viewableScienceType=self.instance.scienceType
            # implementable only matters if it's controlled
            self.showImplemented=True
        else:
            self.fields['scienceType'].widget=forms.TextInput(attrs={'size':'40'})
            self.viewableScienceType=''
            self.showImplemented=False

class ComponentInputForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"120",'rows':"2"}),required=False)
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'size':'24'}),required=True)
    units=forms.CharField(widget=forms.TextInput(attrs={'size':'48'}),required=False)
    cfname=TermAutocompleteField(Vocab,'CFStandardNames',Term,required=False,size=60)
 
    class Meta:
        model=ComponentInput
        exclude=('owner','realm') # we know these
    def __init__(self,*args,**kwargs):       
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='InputTypes')
        self.fields['ctype'].queryset=Term.objects.filter(vocab=v)
        # this can't go in the attributes section, because of import issues, deferring it works ...
           
       
class DataContainerForm(forms.ModelForm):
    ''' This is the form used to edit "files" ... '''
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'45'}),required=False)
    description=forms.CharField(widget=forms.Textarea({'cols':'50','rows':'4'}),required=False)
    class Meta:
        model=DataContainer
        exclude=('centre','dataObject','funder','author','contact','metadataMaintainer')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='FileFormats')
        self.fields['format'].widget=DropDownSingleWidget()
        self.fields['format'].queryset=Term.objects.filter(vocab=v)
        self.fields['experiments'].widget=DropDownWidget()
        self.fields['experiments'].queryset=Experiment.objects.all()
        self.hostCentre=None
    def specialise(self,centre):
        self.fields['reference'].widget=DropDownSingleWidget()
        self.fields['reference'].queryset=Reference.objects.filter(centre=centre)|Reference.objects.filter(centre=None)
    def save(self):
        ''' Need to add the centre, and save the subform too '''
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        o.save()
        return o
    def clean(self):
        ''' Needed to ensure name uniqueness within a centre, and handle the subform '''
        return uniqueness(self,self.hostCentre,'title')

class DataObjectForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'50','rows':'2'}),required=False)
    variable=forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
    cfname=TermAutocompleteField(Vocab,'CFStandardNames',Term,required=False,size=60)
    class Meta:
        model=DataObject
        exclude=('featureType','drsAddress','container')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.hostCentre=None
    def specialise(self,centre):
        self.fields['reference'].queryset=Reference.objects.filter(centre=centre)|Reference.objects.filter(centre=None)
        
class DataHandlingForm(object):
    ''' This is a fudge to allow baseview to think it's dealing with one form, 
    when it's really dealing with two'''
    # Base view will send datacontainer objects as the instance... we need to handle them,
    # and the objects within them, and the request
    DataObjectFormSet=modelformset_factory(DataObject,form=DataObjectForm,can_delete=True)
    def __init__(self,postData=None,instance=None):
        self.cform=DataContainerForm(postData,instance=instance,prefix='cform')
        if instance:
            qset=DataObject.objects.filter(container=instance)
        else:
            qset=DataObject.objects.none()
        self.oform=self.DataObjectFormSet(postData,queryset=qset,prefix='oform')
        self.hostCentre=None
    def is_valid(self):
        return self.cform.is_valid() and self.oform.is_valid()
        
    def specialise(self,constraints):
        self.cform.specialise(constraints)
        for f in self.oform.forms:
            f.specialise(constraints)
    def save(self):
        c=self.cform.save()
        oset=self.oform.save(commit=False)
        for o in oset: 
            o.container=c
            o.save()
        return c
    
    def handleError(self):
        return str(self.cform.errors)+str(self.oform.errors)
    
    def getCentre(self):
        return self.cform.hostCentre
    
    def setCentre(self,val):
        self.oform.hostCentre=val
        self.cform.hostCentre=val
    
    errors=property(handleError,None)
    hostCentre=property(getCentre,setCentre)

class EnsembleForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    class Meta:
        model=Ensemble
        exclude=('simulation')
    def __init__(self,*args,**kwargs):
        logging.debug('initialising ensemble form')
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.fields['etype'].queryset=Term.objects.filter(vocab=Vocab.objects.get(name='EnsembleTypes'))

class EnsembleMemberForm(forms.ModelForm):
    class Meta:
        model=EnsembleMember
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        logging.debug('initialising ensemble set')
        if self.instance:
            # find the set of modifications which are appropriate for the current centre
            etype=self.instance.ensemble.etype
            vet=Vocab.objects.get(name='EnsembleTypes')
            # probably don't need the filter, but just to make sure ...
            pp=Term.objects.filter(vocab=vet).get(name='Perturbed Physics')
            if etype==pp:
                qs=ModelMod.objects.filter(centre=self.instance.ensemble.simulation.centre)
            else:
                qs=InputMod.objects.filter(centre=self.instance.ensemble.simulation.centre)
            self.fields['mod'].queryset=qs  

class ModForm(forms.ModelForm):
    mnemonic=forms.CharField(widget=forms.TextInput(attrs={'size':'25'}))
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    def __init__(self,*args,**kwargs):  
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.hostCentre=None
    def save(self,attr=None):
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        if attr is not None:
            o.__setattr__(attr[0],attr[1])
        o.save()
        return o
    def clean(self):
        ''' Needed to ensure reference name uniqueness within a centre '''
        return uniqueness(self,self.hostCentre,'mnemonic')
        

class InputClosureModForm(forms.ModelForm):
    class Meta:
        model=InputClosureMod
        exclude='targetClosure'  # that's set by the input modd
    def specialise(self):
         if self.instance.targetFile:
            self.fields['target'].queryset=DataObject.objects.filter(container=self.instance.targetFile)
                 
class InputModForm(ModForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    revisedDate=forms.DateField(required=False)
    #revisedClosures=forms.ModelMultipleChoiceField(widget=forms.HiddenInput(),required=True)
    class Meta:
        model=InputMod
        exclude=('centre','mtype')
    def __init__(self,*args,**kwargs):
        ModForm.__init__(self,*args,**kwargs)
        self.ivocab=Vocab.objects.get(name='InputTypes')
        self.ic=Term.objects.filter(vocab=self.ivocab).get(name='InitialCondition')
    def specialise(self,group):
        self.fields['revisedInputs'].queryset=Coupling.objects.filter(parent=group).filter(targetInput__ctype=self.ic)
        self.group=group
        self.simulation=group.simulation
    def save(self):
        f=ModForm.save(self,attr=('mtype',self.ic))
        self.save_m2m()
        return f
    
class InputModIndex(object):
    ''' Used to bundle the form and child formsets together to help base view '''
    closureforms=modelformset_factory(InputClosureMod,form=InputClosureModForm,can_delete=True)
   
    def __init__(self,postData=None,instance=None):
        self.master=InputModForm(postData,instance=instance,prefix='mform')
        self.hostCentre=None
    def specialise(self,simulation):
        self.cg=CouplingGroup.objects.get(simulation=simulation)
        self.s=simulation
        self.master.specialise(self.cg)
    def is_valid(self):
        return self.master.is_valid()
    def save(self):
        m=self.master.save()
        return m
    def handleError(self):
        return self.master.errors
    def getCentre(self):
        return self.master.hostCentre
    def setCentre(self,val):
        self.master.hostCentre=val
     
    errors=property(handleError,None)
    hostCentre=property(getCentre,setCentre)  
      
class ModelModForm(ModForm):
    class Meta:
        model=ModelMod
        exclude=('centre')
    def specialise(self,model):
        self.fields['component'].queryset=Component.objects.filter(model=model)
        ivocab=Vocab.objects.get(name='ModelModTypes')
        self.fields['mtype'].queryset=Term.objects.filter(vocab=ivocab)


class PlatformForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'class':'optin','cols':"80",'rows':"4"}),required=False)
    maxProcessors=forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin','size':5}),required=False)
    coresPerProcessor=forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin','size':5}),required=False)
    class Meta:
        model=Platform
        exclude=('centre','uri','metadataMaintainer')        
        
class ReferenceForm(forms.ModelForm):
    citation=forms.CharField(widget=forms.Textarea({'cols':'140','rows':'2'}))
    #link=forms.URLField(widget=forms.TextInput(attrs={'size':'55'}))
    link=refLinkField(widget=forms.TextInput(attrs={'size':'55'}),required=False)
    class Meta:
        model=Reference
        exclude=('centre',)
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='ReferenceTypes')
        self.fields['refType'].queryset=Term.objects.filter(vocab=v)
        self.hostCentre=None
    def save(self):
        r=forms.ModelForm.save(self,commit=False)
        r.centre=self.hostCentre
        r.save()
        return r
    def specialise(self,centre):
        pass
    def clean(self):
        ''' Needed to ensure reference name uniqueness within a centre '''
        return uniqueness(self,self.hostCentre,'name')
        
class ResponsiblePartyForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    webpage=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    name=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'size':'24'}))
    address=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    uri=forms.CharField(widget=forms.HiddenInput(),required=False)
    class Meta:
        model=ResponsibleParty
        exclude=('centre')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.hostCentre=None
    def clean_uri(self):
        ''' On creating a responsible party we need a uri, once we have one, it should stay the same '''
        data=self.cleaned_data['uri']
        if data == u'': data=atomuri()
        return data
    def save(self):
        r=forms.ModelForm.save(self,commit=False)
        r.centre=self.hostCentre
        r.save()
        return r
               
               
class SimulationForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}),required=False)
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    authorList=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}))
    class Meta:
        model=Simulation
        #the first three are enforced by the workflow leading to the form, the second two are
        #dealt with on other pages. NB: note that if you don't exclude things, then a form
        #will expect them, and set them to None if they don't come back in the post ... a quiet
        #loss of information ...
        exclude=('centre','experiment','uri','modelMod','inputMod','relatedSimulations')
    def specialise(self,centre):
        self.fields['platform'].queryset=Platform.objects.filter(centre=centre)
        self.fields['numericalModel'].queryset=Component.objects.filter(
                            scienceType='model').filter(centre=centre)
        qs=ResponsibleParty.objects.filter(centre=centre)|ResponsibleParty.objects.filter(party=centre)
        for i in ['author','funder','contact']: self.fields[i].queryset=qs                  
    def save(self):
        s=forms.ModelForm.save(self)
        try:
            e=Ensemble.objects.get(simulation=s)
        except:
            #couldn't find it? create it!
            e=Ensemble(simulation=s)
            e.save()
        e.updateMembers()
        return s
        
class SimRelationshipForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':"80",'rows':"2"}),required=False)
    class Meta:
        model=SimRelationship
        exclude=('vocab','sfrom')
    def __init__(self,simulation,*args,**kwargs):
        self.simulation=simulation
        self.vocab=Vocab.objects.get(name='SimRelationships')
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.fields['value'].queryset=Term.objects.filter(vocab=self.vocab)
        self.fields['sto'].queryset=Simulation.objects.filter(centre=self.simulation.centre)
    def clean(self):
        tmp=self.cleaned_data.copy()
        for k in 'value','sto':
            if k in tmp:
                if tmp[k] is None: del tmp[k]
        if 'sto' in tmp or 'value' in tmp:
            if 'sto' not in tmp or 'value' not in tmp:
                raise forms.ValidationError('Need both related simulation and relationship')
        return self.cleaned_data
    def save(self):
        s=forms.ModelForm.save(self,commit=False)
        s.sfrom=self.simulation
        s.save()

class ControlledAttributeForm(forms.Form):
    class Meta:
        exclude=('constraint','ptype','controlled')

class FloatControlledAttributeForm(ControlledAttributeForm):
    value=forms.FloatField(required=True)
    
class StrControlledAttributeForm(ControlledAttributeForm):
    value=forms.CharField(required=True)
    
class XorControlledAttributeForm(ControlledAttributeForm):
    q1=Term.objects.all()
    value=forms.ModelMultipleChoiceField(required=False,queryset=q1,widget=DropDownSingleWidget(attrs={'size':'5'}))
    
class OrControlledAttributeForm(ControlledAttributeForm):
    q1=Term.objects.all()
    value=forms.ModelChoiceField(required=False,queryset=q1,widget=DropDownWidget(attrs={'size':'5'}))
  
class UserAttributeForm(ControlledAttributeForm):
    name=forms.CharField(required=True)
    value=forms.CharField(required=True)
    units=forms.CharField(required=False)
  