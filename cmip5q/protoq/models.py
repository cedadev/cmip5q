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
    def __unicode__(self):
        return self.name
    
#class triple(models.Model):
#    ''' Used for building bidirectional relationships '''
#    ##http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
#    # subject, object, predicate
#    object=models.SlugField(max_length=64)
#    
#    subject=models.ForeignKey(ContentType,related_name='triple_subject')
#    subject_id=models.PositiveIntegerField()
#    subject_object=generic.GenericForeignKey('subject','subject_id')
#    
#    predicate=models.ForeignKey(ContentType,related_name='triple_predicate')
#    predicate_id=models.PositiveIntegerField()
#    predicate_object=generic.GenericForeignKey('predicate','predicate_id')
#   
#    def __unicode__(self):
#        return '%s,%s,%s'%(subject,object,predicate)
    
#class Relation(models.Model):
#    ''' Used for holding uni-directional relationships '''
#    tag=models.SlugField(max_length=64)
#    #relation=models.ForeignKey(ContentType)
#    #relation_id=models.PositiveIntegerField()
#    ##relation_object=generic.GenericForeignKey(ct_field='relation',fk_field='relat#ion_id')
#    content_type = models.ForeignKey(ContentType)
#    object_id = models.PositiveIntegerField()
#    content_object = generic.GenericForeignKey('content_type', 'object_id')
#    # don't know why the former doesn't work, but let's deal
#    # with one problem at a time.#
#
#    def __unicode__(self):
#        return '(%s,%s)'%(self.tag,self.relation_object)
    
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
    
class Experiment(Doc):
    ''' A CMIP5 Experiment '''
    
class Simulation(Doc):
    ''' A CMIP5 Simulation '''
    #models may be used for multiple simulations
    numericalModel=models.ForeignKey(Component)
    ensembleMembers=models.PositiveIntegerField(default=1)
    #each simulation corresponds to one experiment
    experiment=models.ForeignKey(Experiment)
    #expect to set platforms up after we've set up simulations
    platform=models.ForeignKey(Platform,blank=True,null=True)
    #each simulation run by one centre
    centre=models.ForeignKey('Centre')
    
    
class Conformance:
    ''' This relates a numerical requirement to an actual solution in the simulation '''
    uid=models.CharField(max_length=64,unique=True)
    # the identifier of the numerical requirement:
    exptuid=models.CharField(max_length=64)
    # if we didn't use a file, it will be code
    usedFile=models.BooleanField(default=1)
    # so we enter some text if we do a code modification
    ## FIXME: use foreign keys for component ids, not blank strings ...
    codeModDescription=models.TextField(blank=True,null=True)
    # this is the uid of the target component that has been modified (if any has)
    codeModTargetUid=models.CharField(max_length=64,blank=True,null=True)
    # This is the original unmodified component if we know it
    codeOriginalUid=models.CharField(max_length=64,blank=True,null=True)
    
    
class Centre(Doc):
    ''' A CMIP5 modelling centre '''
    
class NumericalRequirement(Doc):
    ''' A numerical Requirement '''
    experiment=models.ForeignKey(Experiment)
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
##
### FORMS FOLLOW
## We only need forms for the things the punters fill in,
## we can use the admin interface for the things we fill in
## (Exxperiment, Centre)
#
class SimulationForm(forms.ModelForm):
    class Meta:
        model=Simulation
        #these are enforced by the workflow leading to the form
        exclude=('centre','experiment',)

class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    geneology=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}),required=False)
    #
    title=forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    contact=forms.CharField(widget=forms.TextInput(attrs={'size':'72'}))
    #uri=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
    scienceType=forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
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
        

    
    
    