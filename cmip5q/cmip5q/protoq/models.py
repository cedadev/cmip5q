from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import forms
from django.forms.models import modelformset_factory

import vocab

class Doc(models.Model):
    ''' Abstract class for general properties '''
    title=models.CharField(max_length=128)
    abbrev=models.SlugField(max_length=20)
    contact=models.EmailField(blank=True)
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
    def __unicode__(self):
        return self.name
    
class Component(Doc):
    ''' A model component '''
    # this is the vocabulary NAME of this component:
    scienceType=models.SlugField(max_length=64,blank=True,null=True)
    #
    implemented=models.BooleanField(default=1)
    visited=models.BooleanField(default=0)
    #
    geneology=models.TextField(blank=True,null=True)
    #
    components=models.ManyToManyField('self',blank=True,null=True,symmetrical=False)
    references=models.ManyToManyField(Reference,blank=True,null=True)
    
    #relations=generic.GenericRelation(Relation,blank=True,null=True)
    centre=models.ForeignKey('Centre',blank=True,null=True)
    
class Platform(Doc):
    ''' Hardware platform on which simulation was run '''
    centre=models.ForeignKey('Centre',blank=True,null=True)
    
class Experiment(models.Model):
    ''' A CMIP5 Experiment '''
    rationale=models.TextField(blank=True,null=True)
    why=models.TextField(blank=True,null=True)
    requirements=models.ManyToManyField('NumericalRequirement',blank=True,null=True)
    docID=models.CharField(max_length=128)
    startDate=models.CharField(max_length=32)
    endDate=models.CharField(max_length=32)
    
    
class NumericalRequirement(models.Model):
    ''' A numerical Requirement '''
    description=models.TextField()
    name=models.CharField(max_length=128)
    type=models.CharField(max_length=32,blank=True,null=True)
    
class Simulation(Doc):
    ''' A CMIP5 Simulation '''
    #models may be used for multiple simulations
    numericalModel=models.ForeignKey(Component)
    ensembleMembers=models.PositiveIntegerField(default=1)
    #each simulation corresponds to one experiment
    experiment=models.ForeignKey(Experiment)
    #platforms
    platform=models.ForeignKey(Platform)
    #each simulation run by one centre
    centre=models.ForeignKey('Centre')
    
class Conformance(models.Model):
    ''' This relates a numerical requirement to an actual solution in the simulation '''
    # centre (for access control)
    centre=models.ForeignKey('Centre')
    # the identifier of the numerical requirement:
    requirement=models.ForeignKey(NumericalRequirement)
    # simulation owning the requirement 
    simulation=models.ForeignKey(Simulation)
    # if we didn't use a file, it will be code
    method=models.CharField(max_length=30)
    # so we enter some text (particuarly if we do a code modification)
    description=models.TextField()
    # this is the target component that has been modified (if any has)
    component=models.ForeignKey(Component,blank=True,null=True)
    # this is the file object that has been used (if any)
    dataObject=models.ForeignKey('DataObject',blank=True,null=True)
    
    
    
class Centre(Doc):
    ''' A CMIP5 modelling centre '''
    

#
##
### Tables for holding internal component parameter values (and parameter options)
##  follow.
##  The basic idea is that a parameter has
##      a name,
##      a value,
##      and a type, from a questionairre controlled type list ...
##      but the type itself can represent a third party controlled type.
##      so, values for type are:
##            "string"
##            "float"
##            "integer"
##            "OR" - any number of the values at an accom
##            "XOR" 
##      and optionally a uri value, which must be present if either rof the vocab types are present"
##      for the moment, the uri value is a "vocab name" and we have a table of those too "

class Vocab(models.Model):
    ''' Holds the values of a choice list aka vocabulary '''
    # this is the "name" of the vocab, called a uri because in the 
    # future I imagine we'll not hold the vocabs internally
    name=models.CharField(max_length=64)
    uri=models.CharField(max_length=64)
    note=models.CharField(max_length=128,blank=True)
    
class Value(models.Model):
    ''' Vocabulary Values, loaded by script, never prompted for via the questionairre '''
    value=models.CharField(max_length=64)
    vocab=models.ForeignKey(Vocab)  
    
class Param(models.Model):
    ''' This is the abstract parameter class'''
    name=models.CharField(max_length=64,blank=False)
    component=models.ForeignKey(Component,null=True,blank=True)
    ptype=models.SlugField(max_length=12,blank=True)
    # still not sure about this ...
    vocab=models.ForeignKey(Vocab,null=True,blank=True)
    value=models.CharField(max_length=512,blank=True)
    
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
    
##
### FORMS FOLLOW
## We only need forms for the things the punters fill in,
## we can use the admin interface for the things we fill in
## (Exxperiment, Centre)
#

class ConformanceForm(forms.ModelForm):
    ''' Handles material needed to establish conformance '''
    mychoices=(
    ('File','External File'),('Code','Modified Code'),('Standard ','Standard Configuration'),)
    method=forms.ChoiceField(choices=mychoices)
    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'2'}))
    class Meta:
        model=Conformance
        # the following are known via the URI used ...
        exclude=('centre','requirement','simulation')

class DataObjectForm(forms.ModelForm):
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'60'}))
    description=forms.CharField(widget=forms.Textarea({'cols':'70','rows':'2'}))
    variable=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=False)
    cftype=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=False)
    class Meta:
        model=DataObject

class SimulationForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea({'cols':"100",'rows':"4"}),required=False)
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    contact=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}))
    class Meta:
        model=Simulation
        #these are enforced by the workflow leading to the form
        exclude=('centre','experiment','uri')

class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    geneology=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    #
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    contact=forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}))
    #uri=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
    scienceType=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
    implemented=forms.BooleanField(required=True)
    class Meta:
        model=Component
        exclude=('centre','uri')
        
        
        

class ReferenceForm(forms.ModelForm):
    class Meta:
        model=Reference
        
class PlatformForm(forms.ModelForm):
    class Meta:
        model=Platform
        
#class ParamForm(ModelForm):
#    class Meta:
#        model=Param
        
ParamFormSet=modelformset_factory(Param,fields=('name','value','ptype'))
        

    
    
    