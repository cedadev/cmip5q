from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import forms
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse

import vocab

class Doc(models.Model):
    ''' Abstract class for general properties '''
    title=models.CharField(max_length=128,blank=True,null=True)
    abbrev=models.SlugField(max_length=20)
    email=models.EmailField(blank=True)
    contact=models.CharField(max_length=128,blank=True,null=True)
    description=models.TextField(blank=True,null=True)
    uri=models.CharField(max_length=64,unique=True)
    def __unicode__(self):
        return self.abbrev
    class Meta:
        abstract=True
  
class Reference(models.Model):
    ''' An academic Reference '''
    name=models.CharField(max_length=24)
    citation=models.TextField(blank=True)
    link=models.URLField(blank=True,null=True)
    refTypes=models.ForeignKey('Vocab',null=True,blank=True,editable=False)
    refType=models.ForeignKey('Value')
    def __unicode__(self):
        return self.name
    
class Component(Doc):
    ''' A model component '''
    # this is the vocabulary NAME of this component:
    scienceType=models.SlugField(max_length=64,blank=True,null=True)
    
    # these next three are to support the questionnaire function
    implemented=models.BooleanField(default=1)
    visited=models.BooleanField(default=0)
    controlled=models.BooleanField(default=0)
    model=models.ForeignKey('self',blank=True,null=True,related_name="parent_model")
    realm=models.ForeignKey('self',blank=True,null=True,related_name="parent_realm")
    isRealm=models.BooleanField(default=False)
    
    # the following are common parameters
    geneology=models.TextField(blank=True,null=True)
    yearReleased=models.IntegerField(blank=True,null=True)
    otherVersion=models.CharField(max_length=128,blank=True,null=True)
    references=models.ManyToManyField(Reference,blank=True,null=True)
    
    # direct children components:
    components=models.ManyToManyField('self',blank=True,null=True,symmetrical=False)
   
    centre=models.ForeignKey('Centre',blank=True,null=True)
    
class ComponentInput(models.Model):
    ''' This class is used to capture the inputs required by a component '''
    handle=models.CharField(max_length=24)
    name=models.CharField(max_length=128)
    #mainly we're going to be interested in boundary condition inputs:
    bc=models.BooleanField(default=True)
    #the component which owns this input (might bubble up from below realm)
    owner=models.ForeignKey(Component,related_name="input_owner")
    #strictly we don't need this, we should be able to get it by parsing
    #the owners for their parent realms, but it's stored when we create
    #it to improve performance:
    realm=models.ForeignKey(Component,related_name="input_realm")
    def __unicode__(self):
        return '%s:%s'%(owner,handle)
    
class Platform(Doc):
    ''' Hardware platform on which simulation was run '''
    centre=models.ForeignKey('Centre')
    compiler=models.CharField(max_length=128)
    vendor=models.CharField(max_length=128)
    compilerVersion=models.CharField(max_length=32)
    maxProcessors=models.IntegerField()
    coresPerProcessor=models.IntegerField()
    operatingSystem=models.CharField(max_length=128)
    hardware=models.ForeignKey('Value',related_name='hardwareVal')
    processor=models.ForeignKey('Value',related_name='processorVal')
    interconnect=models.ForeignKey('Value',related_name='interconnectVal')
    #see http://metaforclimate.eu/trac/wiki/tickets/280
    
class Experiment(models.Model):
    ''' A CMIP5 Experiment '''
    rationale=models.TextField(blank=True,null=True)
    why=models.TextField(blank=True,null=True)
    requirements=models.ManyToManyField('NumericalRequirement',blank=True,null=True)
    docID=models.CharField(max_length=128)
    shortName=models.CharField(max_length=64)
    longName=models.CharField(max_length=256,blank=True,null=True)
    startDate=models.CharField(max_length=32)
    endDate=models.CharField(max_length=32)
    def __unicode__(self):
        return self.docID
    
class NumericalRequirement(models.Model):
    ''' A numerical Requirement '''
    description=models.TextField()
    name=models.CharField(max_length=128)
    type=models.CharField(max_length=32,blank=True,null=True)
    def __unicode__(self):
        return self.name
    
class Simulation(Doc):
    ''' A CMIP5 Simulation '''
    # models may be used for multiple simulations
    # note that we don't need dates, we can those from the data output, assuming
    # data is output for the entire duration. FIXME: might not have access to
    # that information for all of CMIP5. 
    numericalModel=models.ForeignKey(Component)
    ensembleMembers=models.PositiveIntegerField(default=1)
    #each simulation corresponds to one experiment
    experiment=models.ForeignKey(Experiment)
    #platforms
    platform=models.ForeignKey(Platform)
    #each simulation run by one centre
    centre=models.ForeignKey('Centre')
    #
    # enforce the following as required via q'logical validation, not form validation.
    initialCondition=models.ForeignKey('InitialCondition',blank=True,null=True)
    boundaryCondition=models.ManyToManyField('Coupling',blank=True,null=True)
    physicalEnsemble=models.BooleanField(default=False)
    
class Centre(Doc):
    ''' A CMIP5 modelling centre '''
    files=models.ForeignKey('DataObject',blank=True,null=True)

class Vocab(models.Model):
    ''' Holds the values of a choice list aka vocabulary '''
    # this is the "name" of the vocab, called a uri because in the 
    # future I imagine we'll not hold the vocabs internally
    name=models.CharField(max_length=64)
    uri=models.CharField(max_length=64)
    note=models.CharField(max_length=128,blank=True)
    def __unicode__(self):
        return self.name
    
class Value(models.Model):
    ''' Vocabulary Values, loaded by script, never prompted for via the questionairre '''
    value=models.CharField(max_length=64)
    vocab=models.ForeignKey(Vocab)
    def __unicode__(self):  
        return self.value
        
class Param(models.Model):
    ''' This is the abstract parameter class'''
    name=models.CharField(max_length=64,blank=False)
    component=models.ForeignKey(Component,null=True,blank=True)
    ptype=models.SlugField(max_length=12,blank=True)
    # still not sure about this ...
    vocab=models.ForeignKey(Vocab,null=True,blank=True)
    value=models.CharField(max_length=512,blank=True)
    def __unicode__(self):
        return self.name
    
class DataObject(models.Model):
    ''' Holds the data object information agreed in Paris '''
    # a name for drop down file lists:
    name=models.CharField(max_length=64)
    # a link to the object if possible:
    link=models.URLField(blank=True)
    # a free text description
    description=models.TextField()
    # if the data object is a variable within a dataset at the target uri, give the variable
    variable=models.CharField(max_length=128,blank=True)
    # and if possible the CF name
    cftype=models.CharField(max_length=512,blank=True)
    # references (including web pages)
    reference=models.ForeignKey(Reference,blank=True,null=True)
    #format
    format=models.ForeignKey('Value',blank=True,null=True)
    def __unicode__(self):
        return self.name
        
class Coupling(models.Model):
    #parent component, must be a model for CMIP5:
    component=models.ForeignKey(Component)
    #coupling for:
    targetInput=models.ForeignKey(ComponentInput)
    #coupling details
    couplingType=models.ForeignKey('Value',related_name='couplingTypeVal')
    couplingFreqUnits=models.ForeignKey('Value',related_name='couplingFreqUnits')
    couplingFreq=models.IntegerField()
    manipulation=models.TextField(blank=True,null=True)
    #closures
    internalClosures=models.ManyToManyField('InternalClosure',blank=True,null=True,symmetrical=False)
    externalClosures=models.ManyToManyField('ExternalClosure',blank=True,null=True,symmetrical=False)
    def __unicode__(self):
        return 'Coupling %s'%self.targetInput
        
class CouplingClosure(models.Model):
    ''' Handles a specific closure to a component '''
    closed=models.BooleanField(default=False)
    #http://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    spatialRegridding=models.ForeignKey('Value',related_name='%(class)s_SpatialRegridder')
    temporalRegridding=models.ForeignKey('Value',related_name='%(class)s_TemporalRegridder')
    inputDescription=models.TextField(blank=True,null=True)
    def __unicode__(self):
        return 'Closure %s'%target
    class Meta:
        abstract=True
   
class InternalClosure(CouplingClosure): 
    target=models.ForeignKey(Component)

class ExternalClosure(CouplingClosure):
    ''' AKA boundary condition '''
    target=models.ForeignKey('DataObject')
        
class InitialCondition(models.Model):
    ''' Simulation initial condition '''
    description=models.TextField(blank=True,null=True)
    date=models.DateField() # watch out, model calendars ...
    #actually we want to replace this with a choice into CF ... but need to
    #work out how to handle this. The assumption is that the files will be
    #in the archive, so we don't need to ask for them. If we know their
    #CF name, then we know them.
    variables=models.TextField(blank=True,null=True)
    def __unicode__(self):
        return str(self.date)
         
class CodeModification(models.Model):
    mnemonic=models.SlugField()
    component=models.ForeignKey(Component)
    description=models.TextField()
    #we could try and get to the parameter values as well ...
    def __unicode__(self):
        return "%s (%s)"%(self.mnemonic,self.component)

class PhysicalEnsemble(models.Model):
    ensembleDescription=models.TextField(blank=True,null=True)
    codeModification=models.ManyToManyField(CodeModification,blank=True,null=True)
    simulation=models.ForeignKey(Simulation)
    
class Conformance(models.Model):
    ''' This relates a numerical requirement to an actual solution in the simulation '''
    # the identifier of the numerical requirement:
    requirement=models.ForeignKey(NumericalRequirement)
    # simulation owning the requirement 
    simulation=models.ForeignKey(Simulation)
    # conformance type from the controlled vocabulary
    ctype=models.ForeignKey(Value,blank=True,null=True)
    # code modification 
    codeModification=models.ManyToManyField(CodeModification,blank=True,null=True)
    initialCondition=models.ForeignKey(InitialCondition,blank=True,null=True)
    boundaryCondition=models.ForeignKey(Coupling,blank=True,null=True)
    def __unicode__(self):
        return "%s for %s"%(self.ctype,self.requirement)

class EnsembleForm(forms.Form):
    #We don't build it from a model form, because we only really want
    #the description from the user, we do the rest by hand.
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    def clean_description(self):
        data=self.cleaned_data['description']
        if data=='Describe me':
            raise forms.ValidationError('Please change the default')
        return data
    
class CodeModificationForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    class Meta:
        model=CodeModification
    
class InitialConditionForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    variables=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    class Meta:
        model=InitialCondition
        
class BoundaryConditionForm(forms.ModelForm):
    ''' Simulation boundary condition form '''
    inputDescription=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    class Meta:
        model=ExternalClosure
    def specialise(self,model):
        ''' Specialise as it's own method to avoid confusion with POST and GET '''
        pass
       
class CouplingForm(forms.ModelForm):
    manipulation=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    class Meta:
        model=Coupling
        exclude=('component',  # we should always know this
                 'targetInput', # we generate couplings from these 
                )
    #def __init__(self,*args,**kwargs):
    #    forms.ModelForm.__init__(self,*args,**kwargs)
    #    vc=Vocab.objects.get(name='CouplingType')
    #    vu=Vocab.objects.get(name='FreqUnits')
    #    self.fields['couplingType'].queryset=Value.objects.filter(vocab=vc)
    #   self.fields['couplingFreqUnits'].queryset=Value.objects.filter(vocab=vu)
                
class InternalClosureForm(forms.ModelForm):
     inputDescription=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
     class Meta:
         model=InternalClosure
     def __init__(self,*args,**kwargs):
         forms.ModelForm.__init__(self,*args,**kwargs)
         vs=Vocab.objects.get(name='SpatialRegridding')
         vt=Vocab.objects.get(name='TemporalRegridding')
         self.fields['spatialRegridding'].queryset=Value.objects.filter(vocab=vs)
         self.fields['temporalRegridding'].queryset=Value.objects.filter(vocab=vt)
     def specialise(self,model):
         self.fields['target'].queryset=Component.objects.filter(model=model).filter(realm=True)

class ExternalClosureForm(InternalClosureForm):
     class Meta:
         model=ExternalClosure
     def specialise(self,model):
         pass
                
class DataObjectForm(forms.ModelForm):
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'70'}))
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    variable=forms.CharField(widget=forms.TextInput(attrs={'size':'70'}),required=False)
    cftype=forms.CharField(widget=forms.TextInput(attrs={'size':'70'}),required=False)
    class Meta:
        model=DataObject
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='FileFormats')
        self.fields['format'].queryset=Value.objects.filter(vocab=v)

class SimulationForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}),required=False)
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    email=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}))
    contact=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    class Meta:
        model=Simulation
        #these are enforced by the workflow leading to the form
        exclude=('centre','experiment','uri','intialcondition')
    def specialise(self,centre):
        self.fields['platform'].queryset=Platform.objects.filter(centre=centre)
        self.fields['numericalModel'].queryset=Component.objects.filter(
                            scienceType='model').filter(centre=centre)

class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    geneology=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    #
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    email=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}))
    contact=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    scienceType=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
    implemented=forms.BooleanField(required=True)
    yearReleased=forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'}),required=False)
    otherVersion=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}),required=False)
    class Meta:
        model=Component
        exclude=('centre','uri')

class ReferenceForm(forms.ModelForm):
    citation=forms.CharField(widget=forms.Textarea({'cols':'140','rows':'2'}))
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'55'}))
    class Meta:
        model=Reference
        #exclude=('refTypes')
    
class PlatformForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    maxProcessors=forms.IntegerField(widget=forms.TextInput(attrs={'size':5}))
    coresPerProcessor=forms.IntegerField(widget=forms.TextInput(attrs={'size':5}))
    class Meta:
        model=Platform
        exclude=('centre','uri')
        
class ConformanceForm(forms.ModelForm):
    class Meta:
        model=Conformance
        exclude=('simulation') # we know it
    def specialise(self,model,simulation):
        #http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        relevant_components=Component.objects.filter(model=model)
        self.fields['codeModification'].queryset=CodeModification.objects.filter(component__in=relevant_components)
        #self.fields['initialCondition'].queryset
        self.fields['boundaryCondition'].queryset=Coupling.objects.filter(component=model)
    
    
        