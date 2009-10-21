from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import forms
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from protoq.utilities import uniqueness
import uuid
import logging

NEWMINDMAPS=1

class ResponsibleParty(models.Model):
    ''' So we have the flexibility to use this in future versions '''
    name=models.CharField(max_length=128,blank=True)
    abbrev=models.CharField(max_length=25)
    email=models.EmailField(blank=True)
    address=models.TextField(blank=True)
    uri=models.CharField(max_length=64,unique=True)
    centre=models.ForeignKey('Centre',blank=True,null=True) # for access control
    def __unicode__(self):
        return self.abbrev
    
class Centre(ResponsibleParty):
    ''' A CMIP5 modelling centre '''
    # It's such an important entity it gets it's own sub class ...
    # I wanted to preserve the API, but title will need to change to name
    party=models.OneToOneField(ResponsibleParty,parent_link=True,related_name='party')
    def __init__(self,*args,**kwargs):
        ResponsibleParty.__init__(self,*args,**kwargs)

class Doc(models.Model):
    ''' Abstract class for general properties '''
    title=models.CharField(max_length=128,blank=True,null=True)
    abbrev=models.CharField(max_length=25)
    author=models.ForeignKey(ResponsibleParty,blank=True,null=True,related_name='%(class)s_author')
    funder=models.ForeignKey(ResponsibleParty,blank=True,null=True,related_name='%(class)s_funder')
    contact=models.ForeignKey(ResponsibleParty,blank=True,null=True,related_name='%(class)s_contact')
    description=models.TextField(blank=True)
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
    centre=models.ForeignKey('Centre',blank=True,null=True)
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
    isModel=models.BooleanField(default=False)
    
    # the following are common parameters
    geneology=models.TextField(blank=True,null=True)
    yearReleased=models.IntegerField(blank=True,null=True)
    otherVersion=models.CharField(max_length=128,blank=True,null=True)
    references=models.ManyToManyField(Reference,blank=True,null=True)
    
    # direct children components:
    components=models.ManyToManyField('self',blank=True,null=True,symmetrical=False)
   
    centre=models.ForeignKey('Centre',blank=True,null=True)
    
    def validate(self):
        # I don't work yet as I need my local component_id
        ''' Check to see if component is valid. Returns True/False '''
        nm=NumericalModel(Centre.objects.get(id=self.centre_id),component_id)
        CIMDoc=nm.export(recurse=False)
        sct_doc = ET.parse("xsl/BasicChecks.sch")
        schematron = ET.Schematron(sct_doc)
        return schematron.validate(CIMFragment)

    def copy(self,centre,model=None,realm=None):
        ''' Carry out a deep copy of a model '''
        if centre.__class__!=Centre:
            raise ValueError('Invalid centre passed to component copy')
        
        attrs=['title','abbrev','description',
               'scienceType','controlled','isRealm','isModel',
               'author','contact','funder']
        kwargs={}
        for i in attrs: kwargs[i]=self.__getattribute__(i)
        if kwargs['isModel']: 
            kwargs['title']=kwargs['title']+' dup'
            kwargs['abbrev']=kwargs['abbrev']+' dup'
        kwargs['uri']=str(uuid.uuid1())
        kwargs['centre']=centre
        
        new=Component(**kwargs)
        new.save() # we want an id
       
        # now handle the references
        for r in self.references.all():
            new.references.add(r)
       
        if model is None:
            if self.isModel:
                model=new
            else:
                raise ValueError('Deep copy called with invalid model arguments: %s'%self)
        elif realm is None:
            if self.isRealm:
                realm=new
            else:
                raise ValueError('Deep copy called with invalid realm arguments: %s'%self)
        new.model=model
        new.realm=realm
       
        for c in self.components.all():
            r=c.copy(centre,model=model,realm=realm)
            new.components.add(r)
            logging.debug('Added new component %s to component %s (in centre %s, model %s with realm %s)'%(r,new,centre, model,realm))
            
        #### Now we need to deal with the parameter settings too ..
        if NEWMINDMAPS:
            pset=ParamGroup.objects.filter(component=self)
            for p in pset: p.copy(new)
        else:
            pset=Param.objects.filter(component=self)
            for p in pset: p.makeNewCopy(new)
        
        ### And deal with the component inputs too ..
        inputset=ComponentInput.objects.filter(owner=self)
        for i in inputset: i.makeNewCopy(new)
                
        new.save()
        return new
    
class ComponentInput(models.Model):
    ''' This class is used to capture the inputs required by a component '''
    abbrev=models.CharField(max_length=24)
    description=models.TextField(blank=True,null=True)
    #mainly we're going to be interested in boundary condition inputs:
    ctype=models.ForeignKey('Value')
    #the component which owns this input (might bubble up from below realm)
    owner=models.ForeignKey(Component,related_name="input_owner")
    #strictly we don't need this, we should be able to get it by parsing
    #the owners for their parent realms, but it's stored when we create
    #it to improve performance:
    realm=models.ForeignKey(Component,related_name="input_realm")
    constraint=models.ForeignKey('Constraint',null=True,blank=True)
    def __unicode__(self):
        return '%s:%s'%(self.owner,self.abbrev)
    def makeNewCopy(self,component):
        new=ComponentInput(abbrev=self.abbrev,description=self.description,ctype=self.ctype,
                           owner=component,realm=component.realm)
        new.save()
        # if we've made a new input, we need a new coupling
        ci=Coupling(component=component.model,targetInput=new)
        ci.save()

class Constraint(models.Model):
    ''' Used to ensure that something is only used if needed '''
    # This is the constraint as it appeared on input
    note=models.CharField(max_length=256)
    # this is the parameter holding the constraint target
    key=models.ForeignKey('Param',blank=True,null=True)
    # and this is the value it must hold to be a valid constraint (ie TRUE)
    value=models.CharField(max_length=256)
    def __unicode__(self):
        return note
    def isValid(self):
        try:
            return str(self.key.value)==self.value
        except:
            #FIXME: need to make sure we have a value ...
            return False
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
        return self.shortName
    class Meta:
        ordering=('longName',)
    
class NumericalRequirement(models.Model):
    ''' A numerical Requirement '''
    description=models.TextField()
    name=models.CharField(max_length=128)
    ctype=models.ForeignKey('Value',blank=True,null=True)
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
    # following will be used to construct the DOI
    authorList=models.TextField()
    
    # allow some minor mods to match the criteria, how else would it be described?
    modelMod=models.ManyToManyField('ModelMod',blank=True,null=True)
    
    # this next is here in case we need it later, but I think we shouldn't
    inputMod=models.ManyToManyField('InputMod',blank=True,null=True)
    
    def save(self):
        Doc.save(self)
        
    def updateCoupling(self):
        ''' Update my couplings, in case the user has made some changes in the model '''
        #each one of these should appear in one of my boundary conditions.
        modelCouplings=Coupling.objects.filter(component=self.numericalModel).filter(simulation=None)
        myCouplings=Coupling.objects.filter(component=self.numericalModel).filter(simulation=self)
        myOriginals=[i.original for i in myCouplings]
        for m in modelCouplings:
            if m not in myOriginals: 
                r=m.duplicate4sim(self)

    def copy(self,experiment):
        ''' Copy this simulation into a new experiment '''
        s=Simulation(abbrev=self.abbrev+' dup',title='copy', 
                     contact=self.contact, author=self.author, funder=self.funder,
                     description=self.description, authorList=self.authorList,
                     uri=str(uuid.uuid1()),
                     experiment=experiment,numericalModel=self.numericalModel,
                     ensembleMembers=1, platform=self.platform, centre=self.centre,
                     inputMod=self.inputMod,modelMod=self.modelMod)
        s.save()
        #now we need to get all the other stuff related to this simulation
        #couplings:
        myCouplings=Coupling.objects.filter(component=self.numericalModel).filter(simulation=self)
        for m in myCouplings:
            r=m.duplicate4sim(s)
        # conformance:
        # we can't duplicate that, since we don't know the conformance are the same unless we 
        # have a mapping page somewhere ... 
        return s


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
    
class ParamGroup(models.Model):
    ''' This holds either constraintGroups or parameters to link to components '''
    name=models.CharField(max_length=64,default="Attributes")
    component=models.ForeignKey(Component)
    def copy(self,newComponent):
        new=ParamGroup(name=self.name,component=newComponent)
        new.save()
        for constraint in self.constraintgroup_set.all():constraint.copy(new)
    def __unicode__(self):
        return self.name

class ConstraintGroup(models.Model):
    constraint=models.CharField(max_length=256,blank=True,null=True)
    parentGroup=models.ForeignKey(ParamGroup)
    def __unicode__(self):
        if self.constraint: 
            return self.constraint
        else: return '' 
    def copy(self,paramgrp):
        new=ConstraintGroup(constraint=self.constraint,parentGroup=paramgrp)
        new.save()
        for param in self.newparam_set.all(): param.copy(new)
    
class NewParam(models.Model):
    ''' Holds an actual parameter '''
    name=models.CharField(max_length=64,blank=False)
    controlled=models.BooleanField(default=True)
    ptype=models.SlugField(max_length=12,blank=True)
    # lives in 
    constraint=models.ForeignKey(ConstraintGroup)
    # should have definition
    definition=models.CharField(max_length=128,null=True,blank=True)
    # Following used to point to vocabs and their values ...
    # If a vocab is linked, then the value must be from it!
    vocab=models.ForeignKey(Vocab,null=True,blank=True)
    value=models.CharField(max_length=512,blank=True)
    # but it might be a numeric parameter, in which case we have more attributes
    units=models.CharField(max_length=128,null=True,blank=True)
    def __unicode__(self):
        return self.name
    def copy(self,constraint):
        new=NewParam(name=self.name,constraint=constraint,ptype=self.ptype,controlled=self.controlled,
                      vocab=self.vocab,value=self.value,definition=self.definition,units=self.units)
        new.save()
    
class Param(models.Model):
    ''' This is the abstract parameter class'''
    name=models.CharField(max_length=64,blank=False)
    controlled=models.BooleanField(default=True)
    ptype=models.SlugField(max_length=12,blank=True)
    # applies to
    component=models.ForeignKey(Component,null=True,blank=True)
    #following used to inform users about choices:
    info=models.CharField(max_length=256,null=True,blank=True)
    # constraint note
    myconstraint=models.CharField(max_length=256,null=True,blank=True)
    # Following used to point to vocabs and their values ...
    # If a vocab is linked, then the value must be from it!
    vocab=models.ForeignKey(Vocab,null=True,blank=True)
    value=models.CharField(max_length=512,blank=True)
    # but it might be a numeric parameter, in which case we have more attributes
    definition=models.CharField(max_length=128,null=True,blank=True)
    units=models.CharField(max_length=128,null=True,blank=True)
    def __unicode__(self):
        return self.name
    def makeNewCopy(self,component):
        new=Param(name=self.name,component=component,ptype=self.ptype,controlled=self.controlled,
                      vocab=self.vocab,value=self.value,definition=self.definition,
                      info=self.info,myconstraint=self.myconstraint,units=self.units)
        new.save()
    
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
    #centre that owns this data object
    centre=models.ForeignKey('Centre')
    def __unicode__(self):
        return self.name
        
class Coupling(models.Model):
    # parent component, must be a model for CMIP5:
    component=models.ForeignKey(Component)
    # coupling for:
    targetInput=models.ForeignKey(ComponentInput)
    # may also be associated with a simulation, in which case there is an original
    simulation=models.ForeignKey(Simulation,blank=True,null=True)
    original=models.ForeignKey('Coupling',blank=True,null=True)
    # coupling details for boundary conditions
    couplingType=models.ForeignKey('Value',related_name='%(class)s_couplingTypeVal',blank=True,null=True)
    couplingFreqUnits=models.ForeignKey('Value',related_name='%(class)s_couplingFreqUnits',blank=True,null=True)
    couplingFreq=models.IntegerField(blank=True,null=True)
    manipulation=models.TextField(blank=True,null=True)
    def __unicode__(self):
        if self.simulation:
            return 'I/O4for%s(in %s)'%(self.targetInput,self.simulation)
        else:
            return 'I/Ofor%s'%self.targetInput
    def duplicate4sim(self,simulation):
        '''Make a copy of self, and associate with a simulation'''
        # first make a copy of self
        args=['component','targetInput',
          'couplingType','couplingFreq','couplingFreqUnits',
          'manipulation']
        kw={'original':self,'simulation':simulation}
        for a in args:kw[a]=self.__getattribute__(a)
        new=Coupling(**kw)
        new.save()
        # and now copy all the original closures
        # icset=InternalClosure.objects.filter(coupling=self)
        # ecset=ExternalClosure.objects.filter(coupling=self)
        # for i in icset:
        #    i.makeNewCopy(self)
        # for i in ecset:
        #    i.makeNewCopy(self)
        # Actually, we'll let the user decide to do this in the form ...
        return new
    
class CouplingClosure(models.Model):
    ''' Handles a specific closure to a component '''
    # we don't need a closed attribute, since the absence of a target means it's open.
    coupling=models.ForeignKey(Coupling,blank=True,null=True)
    #http://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    spatialRegridding=models.ForeignKey('Value',related_name='%(class)s_SpatialRegridder')
    temporalRegridding=models.ForeignKey('Value',related_name='%(class)s_TemporalRegridder')
    inputDescription=models.TextField(blank=True,null=True)
   
    def makeNewCopy(self,coupling):
        ''' Copy closure to a new coupling '''
        kw={'coupling':coupling}
        for key in ['spatialRegridding','temporalRegridding','inputDescription','target']:
            kw[key]=self.__getattribute__(key)
        new=self.__class__(**kw)
        new.save()
    class Meta:
        abstract=True

class InternalClosure(CouplingClosure): 
    target=models.ForeignKey(Component,blank=True,null=True)
    def __unicode__(self):
        return 'iClosure %s'%self.target
    
class ExternalClosure(CouplingClosure):
    ''' AKA boundary condition '''
    target=models.ForeignKey('DataObject',blank=True,null=True)
    def __unicode__(self):
        return 'eClosure %s'%self.target    
        

class Ensemble(models.Model):
    description=models.TextField(blank=True,null=True)
    etype=models.ForeignKey(Value,blank=True,null=True)
    simulation=models.ForeignKey(Simulation)
    def updateMembers(self):
        ''' Make sure we have enough members, this needs to be called if the
        simulation changes it's mind over the number of members '''
        objects=self.ensemblemember_set.all()
        n=len(objects)
        nShouldBe=self.simulation.ensembleMembers
        ndif=n-nShouldBe
        for i in range(abs(ndif)): 
            if ndif >0:
                objects[-1].delete()
            elif ndif < 0:
                e=EnsembleMember(ensemble=self,memberNumber=n+i+1)
                e.save()
    
class EnsembleMember(models.Model):
    ensemble=models.ForeignKey(Ensemble,blank=True,null=True)
    memberNumber=models.IntegerField()
    mod=models.ForeignKey('Modification',blank=True,null=True)
    def __unicode__(self):
        return '%s ensemble member %s'%(self.ensemble.simulation,self.memberNumber)
    
class Conformance(models.Model):
    ''' This relates a numerical requirement to an actual solution in the simulation '''
    # the identifier of the numerical requirement:
    requirement=models.ForeignKey(NumericalRequirement)
    # simulation owning the requirement 
    simulation=models.ForeignKey(Simulation)
    # conformance type from the controlled vocabulary
    ctype=models.ForeignKey(Value)
    #
    mod=models.ManyToManyField('Modification',blank=True,null=True)
    coupling=models.ManyToManyField(Coupling,blank=True,null=True)
    # notes
    description=models.TextField(blank=True,null=True)
    def __unicode__(self):
        return "%s for %s"%(self.ctype,self.requirement)
    
class Modification(models.Model):
    mnemonic=models.SlugField()
    mtype=models.ForeignKey(Value)
    description=models.TextField()
    centre=models.ForeignKey(Centre)
    def __unicode__(self):
        return '%s(%s)'%(self.mnemonic,self.mtype)
    
class InputMod(Modification):
    ''' Simulation initial condition '''
    # could need a date to override the date in the file for i.c. ensembles.
    date=models.DateField(blank=True,null=True) # watch out, model calendars
    # could be to multiple inputs ... otherwise it'd get untidy
    inputs=models.ManyToManyField(Coupling,blank=True,null=True)
         
class ModelMod(Modification):
    #we could try and get to the parameter values as well ...
    component=models.ForeignKey(Component)
        
class ModForm(forms.ModelForm):
    mnemonic=forms.CharField(widget=forms.TextInput(attrs={'size':'25'}))
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    def __init__(self,*args,**kwargs):  
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.hostCentre=None
    def save(self):
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        o.save()
    def clean(self):
        ''' Needed to ensure reference name uniqueness within a centre '''
        return uniqueness(self,self.hostCentre,'mnemonic')
        
class ModelModForm(ModForm):
    class Meta:
        model=ModelMod
        exclude=('centre')
    def specialise(self,model):
        self.fields['component'].queryset=Component.objects.filter(model=model)
        ivocab=Vocab.objects.get(name='ModelModTypes')
        self.fields['mtype'].queryset=Value.objects.filter(vocab=ivocab)
          
class InputModForm(ModForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    class Meta:
        model=InputMod
        exclude=('centre')
    def specialise(self,simulation):
        self.fields['inputs'].queryset=Coupling.objects.filter(simulation=simulation)
        ivocab=Vocab.objects.get(name='InputTypes')
        self.fields['mtype'].queryset=Value.objects.filter(vocab=ivocab)
        
class ConformanceForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"3"}),required=False)
    class Meta:
        model=Conformance
        exclude=('simulation') # we know it
    def specialise(self,simulation):
        #http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        relevant_components=Component.objects.filter(model=simulation.model)
        self.fields['mod'].queryset=CodeModification.objects.filter(component__in=relevant_components)
        self.fields['coupling'].queryset=Coupling.objects.filter(simulation=simulation)
        v=Vocab.objects.get(name='ConformanceTypes')
        self.fields['ctype'].queryset=Value.objects.filter(vocab=v)
       
class EnsembleForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}))
    class Meta:
        model=Ensemble
        exclude=('simulation')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.fields['etype'].queryset=Value.objects.filter(vocab=Vocab.objects.get(name='EnsembleTypes'))

class CouplingForm(forms.ModelForm):
    manipulation=forms.CharField(widget=forms.Textarea({'cols':'120','rows':'2'}),required=False)
    class Meta:
        model=Coupling
        exclude=('component',  # we should always know this
                 'targetInput', # we generate couplings from these 
                 'simulation', # we hold these across ...
                 'original'
                )
class InternalClosureForm(forms.ModelForm):
     inputDescription=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
     class Meta:
         model=InternalClosure
     def specialise(self):
         pass

class ExternalClosureForm(InternalClosureForm):
     inputDescription=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
     class Meta:
         model=ExternalClosure
     def specialise(self):
         pass
                
class DataObjectForm(forms.ModelForm):
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'70'}))
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    variable=forms.CharField(widget=forms.TextInput(attrs={'size':'70'}),required=False)
    cftype=forms.CharField(widget=forms.TextInput(attrs={'size':'70'}),required=False)
    class Meta:
        model=DataObject
        exclude=('centre',)
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='FileFormats')
        self.fields['format'].queryset=Value.objects.filter(vocab=v)
        self.hostCentre=None
    def save(self):
        ''' Need to add the centre '''
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        o.save()
    def clean(self):
        ''' Needed to ensure reference name uniqueness within a centre '''
        return uniqueness(self,self.hostCentre,'name')
        
class SimulationForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}),required=False)
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    authorList=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}))
    class Meta:
        model=Simulation
        #these are enforced by the workflow leading to the form
        exclude=('centre','experiment','uri')
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

class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    
    #implemented=forms.BooleanField(required=True)
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    geneology=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    #
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
   
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


class ReferenceForm(forms.ModelForm):
    citation=forms.CharField(widget=forms.Textarea({'cols':'140','rows':'2'}))
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'55'}))
    class Meta:
        model=Reference
        exclude=('centre',)
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='Reference Types Vocab')
        self.fields['refType'].queryset=Value.objects.filter(vocab=v)
        self.hostCentre=None
    def save(self):
        r=forms.ModelForm.save(self,commit=False)
        r.centre=self.hostCentre
        r.save()
    def specialise(self,arg):
        ''' Arg is dummy argument, we had specialisation at initialisation '''       
        pass
    def clean(self):
        ''' Needed to ensure reference name uniqueness within a centre '''
        return uniqueness(self,self.hostCentre,'name')
    
class PlatformForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    maxProcessors=forms.IntegerField(widget=forms.TextInput(attrs={'size':5}))
    coresPerProcessor=forms.IntegerField(widget=forms.TextInput(attrs={'size':5}))
    class Meta:
        model=Platform
        exclude=('centre','uri')
        
class ComponentInputForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"2"}),required=False)
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'size':'24'}))
    class Meta:
        model=ComponentInput
        exclude=('owner','realm') # we know these
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='InputTypes')
        self.fields['ctype'].queryset=Value.objects.filter(vocab=v)
    
class ResponsiblePartyForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}),required=False)
    name=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'size':'24'}))
    address=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    class Meta:
        model=ResponsibleParty
        exclude=('uri','centre')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.hostCentre=None
    def save(self):
        r=forms.ModelForm.save(self,commit=False)
        r.centre=self.hostCentre
        r.save()
        
class EnsembleMemberForm(forms.ModelForm):
    class Meta:
        model=EnsembleMember
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        if self.instance:
            # find the set of modifications which are appropriate for the current centre
            etype=self.instance.ensemble.etype
            vet=Vocab.objects.get(name='EnsembleTypes')
            # probably don't need the filter, but just to make sure ...
            pp=Value.objects.filter(vocab=vet).get(name='PerturbedPhysics')
            if etype==pp:
                qs=ModelMods.filter(centre=self.instance.ensemble.simulation.centre)
            else:
                qs=InputMods.filter(centre=self.instance.ensemble.simulation.centre)
            self.fields['mod'].queryset=qs
    
    
