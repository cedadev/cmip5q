from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django import forms
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from django.db.models.query import CollectedObjects, delete_objects
from django.db.models.fields.related import ForeignKey
from lxml import etree as ET

from django.db.models import permalink


from atom import Feed
from modelUtilities import uniqueness, refLinkField

from protoq.cimHandling import *


import uuid
import logging

def soft_delete(obj,simulate=False):
    ''' This method provided to use to override native model deletes to avoid
    cascade on delete ... the first requirement is only in responsible parties,
    but it may exist elsewhere, so we put it up here as a standalone method.
    If simulate is passed as true, we don't actually do the delete ... but
    see if we could have done it.
          The method returns a tuple boolean and dict. The boolean will be true if 
    it is possible to delete the object (nothing links to it). If the booleaan
    is false, then the dict is a dictionary keyed by models into instances which link 
    to it, and which need to be unlinked before a delete can occur.'''
    # with help from stack overflow
    
    assert obj._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
                      obj._meta.object_name, obj._meta.pk.attname)

    # My first attempt to do this was simply to override the django delete 
    # method and only delete the actual instance, but this can leave the
    # related objects with hanging links to nothing ... which can then
    # be replaced with the *wrong* objects ... so we either have an error
    # or wrong data ... no, no, no ...
    # seen_objs = CollectedObjects()
    # seen_objs.add(model=obj.__class__, pk=obj.pk, obj=obj, parent_model=None)
    # delete_objects(seen_objs)

    on_death_row = CollectedObjects()
    obj._collect_sub_objects(on_death_row)
    # and ideally clear them all ... but that's hard, and impossible if
    # they don't have null=True ... wait til this gets fixed in django.
    # Meanwhile just return the list of direct linkers 
    # NB: odr={klass1:{id1:instance, id2:instance ...},klass2:{...}}
    klass=obj.__class__
    n=0  # number of objects to be deleted
    for k in on_death_row.unordered_keys():
        n+=len(on_death_row[k]) 
    if n<>1:
        #delve into the metadata to find out what managers point at this model,
        #then use all those to filter out direct relationships to this one.
        related_models=on_death_row.keys()
        # now find all the foreign keys
        directly_linked_models=[]
        fkeys={}
        linkdict={}
        for model in related_models:
            for f in model._meta.fields:
                if isinstance(f, ForeignKey) and f.rel.to == klass: 
                    if model not in directly_linked_models:directly_linked_models.append(model)
                    # get the foreign keys for later use 
                    if model in fkeys:
                        if f not in fkeys[model]: 
                            fkeys[model].append(f)
                    else:
                        fkeys[model]=[f]
        # parse the instances to check they link to this one
        # start by rejecting models which don't actually have a foreign key into this objects class
        for model in related_models:
            if model not in directly_linked_models: del(on_death_row.data[model])
        # now parse the instances and see if they have any direct link to this one (they might
        # be in the list because they link to objects that link to this one, even though they have fks
        # that would allow direct links).
        # it's probably be cleaner to go backwards ... now we know the foreign keys, we should
        # be able to get querysets and see if the object is in the queryset ... but this works too.
        for model in on_death_row.unordered_keys():
            # find all the foreign keys to the object.
            for id in on_death_row.data[model]:
                referer=on_death_row.data[model][id]
                for fk in fkeys[model]:
                    fk_value = getattr(referer, "%s_id" % fk.name)
                    if fk_value is not None:
                        mname=model._meta.module_name
                        if mname not in linkdict: linkdict[mname]=[] 
                        linkdict[mname].append(referer)
        return False,linkdict
    else:
        if not simulate: delete_objects(on_death_row)
        return True,{}

   
class EditHistoryEvent(models.Model):
    ''' Used for edit history event logging '''
    eventDate=models.DateField(auto_now_add=True,editable=False)
    eventParty=models.ForeignKey('ResponsibleParty')
    eventAction=models.TextField(blank=True)
    # following will only means something to whatever creates the event.
    eventIdentifier=models.CharField(max_length=128)

class Fundamentals(models.Model):
    ''' These is an abstract class carrying fundamentals in common between CIM documents
    as currently described in the questionnaire, and CIM documents as exported from the
    questionnaire. It's a convenience class for the questionnaire alone '''
    # The URI should only change if the thing described by the document changes.
    # That is, once assigned, the URI never changes, and once exported, the document should persist.
    # If the thing itself changes, we should copy the document, give it a new URI, and update it ...
    uri=models.CharField(max_length=64,unique=True,editable=False)    
    # However, we can have descriptions which differ because the way we describe it has changed,
    # if that happens, we should modify the version identifier which follows AND the documentVersion.
    metadataVersion=models.CharField(max_length=128,editable=False)
    # The following should only be updated when the document is valid, and the document has
    # been exported as a new version. However, note that while it is possible in principle for
    # this to change with subcomponents, it's not likely as currently implemented.
    documentVersion=models.IntegerField(default=1,editable=False)
    
    class Meta:
        abstract=True
 
class CIMObject (Fundamentals):
    ''' This is an exported CIM object. Once exported, the questionnaire can't molest it,
    but it's included here, because the questionnaire can return it '''
    cimtype=models.CharField(max_length=64)
    xmlfile=models.FileField(upload_to='bnl')
    # These are update by the parent doc, which is why they're not "fundamentals"
    created=models.DateField()
    updated=models.DateField()
    
class Doc(Fundamentals):
    ''' Abstract class for general properties of the CIM documents handled in the questionnaire '''
    
    # Parties (all documents are associated with a centre)
    centre=models.ForeignKey('Centre',blank=True,null=True)
    author=models.ForeignKey('ResponsibleParty',blank=True,null=True,related_name='%(class)s_author')
    funder=models.ForeignKey('ResponsibleParty',blank=True,null=True,related_name='%(class)s_funder')
    contact=models.ForeignKey('ResponsibleParty',blank=True,null=True,related_name='%(class)s_contact')
    metadataMaintainer=models.ForeignKey('ResponsibleParty',blank=True,null=True,
                       related_name='%(class)s_metadataMaintainer')
    
    title=models.CharField(max_length=128,blank=True,null=True)
    abbrev=models.CharField(max_length=25)
    description=models.TextField(blank=True)
   
    # next two are used to calculate the status bar, and are filled in by the validation software
    validErrors=models.IntegerField(default=-1,editable=False)
    numberOfValidationChecks=models.IntegerField(default=0,editable=False)
    # following is used by the user to declare the document is "ready"
    isComplete=models.BooleanField(default=False)
    # to be used for event histories:
    editHistory=models.ManyToManyField(EditHistoryEvent,blank=True,null=True)
    # next two are automagically populated
    created=models.DateField(auto_now_add=True,editable=False)
    updated=models.DateField(auto_now=True,editable=False)
    class Meta:
        abstract=True
        ordering=['abbrev','title']
        
    def status(self):
        ''' Return a percentage completion in terms of validation '''
        if self.validErrors<>-1 and self.numberOfValidationChecks<>0:
            return 100.0*(1.0-float(self.validErrors)/self.numberOfValidationChecks)
        else: return 0.0
        # FIXME: and eventually see if we have a children attribute and sum them up ...
        
    def xmlobject(self):
        ''' Return an lxml object view of me '''
        from protoq.Translator import Translator  # needs to be deferred down here to avoid circularity
        translator=Translator()
        return translator.q2cim(self,docType=self._meta.module_name)
    
    def xml(self):
        ''' Return an xml string version of me '''
        if not self.XMLO: self.XMLO=self.xmlobject()
        return ET.tostring(self.XMLO,pretty_print=True)
    
    def validate(self):
        ''' All documents should be validatable '''
        v=Validator()
        self.XMLO=self.xmlobject()
        v.validateDoc(self.XMLO,cimtype=self._meta.module_name)
        self.validErrors=v.nInvalid
        self.numberOfValidationChecks=v.nChecks
        logging.debug("%s validate checks=%s"%(self._meta.module_name,self.numberOfValidationChecks))
        logging.debug("%s validate errors=%s"%(self._meta.module_name,self.validErrors))
        return v.valid,v.errorsAsHtml()
# FIXME: This moved from component to here ... needs something done eventually ...
#    def validate(self):
#        # I don't work yet as I need my local component_id
#       ''' Check to see if component is valid. Returns True/False '''
#        nm=NumericalModel(Centre.objects.get(id=self.centre_id),component_id)
#        CIMDoc=nm.export(recurse=False)
#       sct_doc = ET.parse("xsl/BasicChecks.sch")
#        schematron = ET.Schematron(sct_doc)
#        return schematron.validate(CIMFragment)
    
        
    def export(self):
        ''' Make available for export in the atom feed '''
        # first redo validation to make sure this really is ok
        valid,html=self.validate()
        self.isComplete=valid
        # now store the document ...
        keys=['uri','metadataVersion','documentVersion','created','updated']
        attrs={}
        for key in keys: attrs[key]=self.__getattribute__(key)
        cfile=CIMObject(**attrs)
        cfile.cimtype=self._meta.module_name
        cfile.xmlFile=self.xml()
        cfile.save()
    
    def __unicode__(self):
        return self.abbrev
   
    def save(self,*args,**kwargs):
        ''' Used to decide what to do about versions. We only increment the document version
        number with changes once the document is considered to be complete and valid '''
        if self.isComplete:  
            self.isComplete=False
            self.documentVersion+=1
            self.validErrors=-1   # now force a revalidation before any future document incrementing.
        if 'eventParty' in kwargs:
            self.editHistory.add(EditHistoryEvent(eventParty=kwargs['eventParty'],eventIdentifier=self.documentVersion))
        return models.Model.save(self,*args,**kwargs)
    
    def delete(self,*args,**kwargs):
        ''' Avoid deleting documents which have foreign keys to this instance'''
        soft_delete(self,*args,**kwargs)
    # how can you get at me?:
    #@models.permalink
    #def get_absolute_url(self):   
    #    return  ('/display/%s/%s'%[self._meta.module_name,self.uri])
    
    # the following three url views exploit the get_absolute_url defined in the subclasses.
    def urlxml(self):
        return('%s_XML'%self._meta.module_name,[str(self.centre.id),str(self.id),])
    urlxml=permalink(urlxml)
 
  
class ResponsibleParty(models.Model):
    ''' So we have the flexibility to use this in future versions '''
    name=models.CharField(max_length=128,blank=True)
    webpage=models.CharField(max_length=128,blank=True)
    abbrev=models.CharField(max_length=25)
    email=models.EmailField(blank=True)
    address=models.TextField(blank=True)
    uri=models.CharField(max_length=64,unique=True)
    centre=models.ForeignKey('Centre',blank=True,null=True) # for access control
    def __unicode__(self):
        return self.abbrev
    def delete(self,*args,**kwargs):
        return soft_delete(self,*args,**kwargs)
    class Meta:
        ordering=['abbrev','name','email']
    
class Centre(ResponsibleParty):
    ''' A CMIP5 modelling centre '''
    # It's such an important entity it gets it's own sub class ...
    # I wanted to preserve the API, but title will need to change to name
    party=models.OneToOneField(ResponsibleParty,parent_link=True,related_name='party')
    def __init__(self,*args,**kwargs):
        ResponsibleParty.__init__(self,*args,**kwargs)
        
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
    def delete(self,*args,**kwargs):
        soft_delete(self,*args,**kwargs)
    class Meta:
        ordering=['name','citation']
    
class Component(Doc):
    ''' A model component '''
    # this is the vocabulary NAME of this component:
    scienceType=models.SlugField(max_length=64,blank=True,null=True)
    
    # these next four are to support the questionnaire function
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
             
             
#    def status(self):
#            
    


    def copy(self,centre,model=None,realm=None):
        ''' Carry out a deep copy of a model '''
        # currently don't copys here ...
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
        new.save() # we want an id, even though we might have one already ... 
        #if new.isModel: print '2',new.couplinggroup_set.all()
       
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
            logging.debug('About to add a sub-component to component %s (in centre %s, model %s with realm %s)'%(new,centre, model,realm))
            r=c.copy(centre,model=model,realm=realm)
            new.components.add(r)
            logging.debug('Added new component %s to component %s (in centre %s, model %s with realm %s)'%(r,new,centre, model,realm))
            
        pset=ParamGroup.objects.filter(component=self)
        for p in pset: p.copy(new)
        
        ### And deal with the component inputs too ..
        inputset=ComponentInput.objects.filter(owner=self)
        for i in inputset: i.makeNewCopy(new)
        new.save()        
        return new
    
    def couplings(self,simulation=None):
        ''' Return a coupling set for me, in a simulation or not '''
        if not self.isModel:
            raise ValueError('No couplings for non "Model" components')
        mygroups=self.couplinggroup_set.all()
        if len(mygroups):
            cg=mygroups.get(simulation=simulation)
            return Coupling.objects.filter(parent=cg)
        else: return []
        
    def save(self,*args,**kwargs):
        ''' Create a coupling group on first save '''
        cgload=0
        if self.isModel and self.id is None: cgload=1
        Doc.save(self,*args,**kwargs)
        if cgload:
            cg=CouplingGroup(component=self)
            cg.save()
    
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
    #constraint=models.ForeignKey('Constraint',null=True,blank=True)
    cfname=models.ForeignKey('Value',blank=True,null=True,related_name='input_cfname')
    units=models.CharField(max_length=64,blank=True)
    
    def __unicode__(self):
        return '%s (%s)'%(self.abbrev, self.owner)
    def makeNewCopy(self,component):
        new=ComponentInput(abbrev=self.abbrev,description=self.description,ctype=self.ctype,
                           owner=component,realm=component.realm,
                           cfname=self.cfname,units=self.units)
        new.save()
        # if we've made a new input, we need a new coupling
        cg=CouplingGroup.objects.filter(simulation=None).get(component=component.model)
        ci=Coupling(parent=cg,targetInput=new)
        ci.save()
    class Meta:
        ordering=['abbrev']

class Platform(Doc):
    ''' Hardware platform on which simulation was run '''
    compiler=models.CharField(max_length=128)
    vendor=models.CharField(max_length=128)
    compilerVersion=models.CharField(max_length=32)
    maxProcessors=models.IntegerField(null=True,blank=True)
    coresPerProcessor=models.IntegerField(null=True,blank=True)
    operatingSystem=models.CharField(max_length=128,blank=True)
    hardware=models.ForeignKey('Value',related_name='hardwareVal',null=True,blank=True)
    processor=models.ForeignKey('Value',related_name='processorVal',null=True,blank=True)
    interconnect=models.ForeignKey('Value',related_name='interconnectVal',null=True,blank=True)
    #see http://metaforclimate.eu/trac/wiki/tickets/280
    
class ClosedDateRange(models.Model):
    startDate=models.CharField(max_length=32,blank=True,null=True)
    endDate=models.CharField(max_length=32,blank=True,null=True)
    length=models.FloatField(blank=True,null=True)  # years
    calendar=models.ForeignKey('Value',blank=True,null=True)
    def __unicode__(self):
        return '%s to %s (%sy)'%(self.startDate,self.endDate,self.length)

class Experiment(Doc):
    ''' A CMIP5 Numerical Experiment '''
    rationale=models.TextField(blank=True,null=True)
    requirements=models.ManyToManyField('NumericalRequirement',blank=True,null=True)
    requiredDuration=models.ForeignKey(ClosedDateRange,blank=True,null=True)
    requiredCalendar=models.ForeignKey('Value',blank=True,null=True,related_name='experiment_calendar')
    #used to identify groups of experiments
    memberOf=models.ForeignKey('Experiment',blank=True,null=True)
    def __unicode__(self):
        return self.abbrev

class NumericalRequirement(models.Model):
    ''' A numerical Requirement '''
    docid=models.CharField(max_length=64)
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
   
    # following will be used to construct the DOI
    authorList=models.TextField()
    
    # allow some minor mods to match the criteria, how else would it be described?
    modelMod=models.ManyToManyField('ModelMod',blank=True,null=True)
    
    # this next is here in case we need it later, but I think we shouldn't
    inputMod=models.ManyToManyField('InputMod',blank=True,null=True)
    
    def save(self):
        Doc.save(self)
        
    def updateCoupling(self):
        ''' Update my couplings, in case the user has added some inputs (and hence couplings)
        in the numerical model, but note that updates to existing input couplings in
        numerical models are not propagated to the simuations already made with them. '''
        # first, do we have our own coupling group yet?
        cgs=self.couplinggroup_set.all()
        if len(cgs): 
            # we've already got a coupling group, let's update it
            assert(len(cgs)==1,'Simulation %s should only have one coupling group'%self) 
            cgs=cgs[0]
            modelCouplings=self.numericalModel.couplings()
            myCouplings=self.numericalModel.couplings(self)
            myOriginals=[i.original for i in myCouplings]
            for m in modelCouplings:
                if m not in myOriginals: 
                    r=m.copy(cgs)
        else:
            # get the model coupling group ... and copy it.
            # it's possible we might be doing this before there is a modelling group
            mcgs=self.numericalModel.couplinggroup_set.all()
            if len(mcgs)==0: 
                pass # nothing to do
                cgs=None # I'm not sure this should ever happen any more ...
            else:
                cgs=mcgs.get(simulation=None)
                cgs=cgs.duplicate4sim(self)
        return cgs  # it's quite useful to get this back (e.g. for resetclosures etc)

    def copy(self,experiment):
        ''' Copy this simulation into a new experiment '''
        s=Simulation(abbrev=self.abbrev+' dup',title='copy', 
                     contact=self.contact, author=self.author, funder=self.funder,
                     description=self.description, authorList=self.authorList,
                     uri=str(uuid.uuid1()),
                     experiment=experiment,numericalModel=self.numericalModel,
                     ensembleMembers=1, platform=self.platform, centre=self.centre)
        s.save()
        #now we need to get all the other stuff related to this simulation
        for mm in self.inputMod.all():s.inputMod.add(mm)
        for mm in self.modelMod.all():s.modelMod.add(mm)
        s.save() # I don't think I need to do this ... but to be sure ...
        #couplings:
        myCouplings=CouplingGroup.objects.filter(component=self.numericalModel).filter(simulation=self)
        for m in myCouplings:
            r=m.duplicate4sim(s)
        # conformance:
        # we can't duplicate that, since we don't know the conformance are the same unless we 
        # have a mapping page somewhere ... 
        return s
        
    def resetConformances(self):
        # we need to set up the conformances or reset them.
        existingConformances=Conformance.objects.filter(simulation=self)
        for c in existingConformances:c.delete()
        ctypes=Vocab.objects.get(name='ConformanceTypes')
        defaultConformance=None#Value.objects.filter(vocab=ctypes).get(value='Via Inputs')
        reqs=self.experiment.requirements.all()
        for r in reqs:
            c=Conformance(requirement=r,simulation=self, ctype=defaultConformance)
            c.save()
    
    def resetCoupling(self,closures=False):
        # we had some couplings, but we need to get rid of them for some reason
        # (usually because we've just change model)
        cgs=self.couplinggroup_set.all()
        if len(cgs)<>0:
            assert(len(cgs)==1,'Expect only one coupling group for simulation %s'%self)
            cg=cgs[0]
            cg.delete()
        # now put back the ones from the model
        cg=self.updateCoupling()
        if closures:cg.propagateClosures()

        
class Vocab(models.Model):
    ''' Holds the values of a choice list aka vocabulary '''
    # this is the "name" of the vocab, called a uri because in the 
    # future I imagine we'll not hold the vocabs internally
    name=models.CharField(max_length=64)
    uri=models.CharField(max_length=64)
    note=models.CharField(max_length=128,blank=True)
    version=models.CharField(max_length=64,blank=True)
    definition=models.TextField(blank=True)
    def __unicode__(self):
       return self.name
    class Meta:
        ordering=('name',)
    
class Value(models.Model):
    ''' Vocabulary Values, loaded by script, never prompted for via the questionairre '''
    value=models.CharField(max_length=64)
    vocab=models.ForeignKey('Vocab')
    definition=models.TextField(blank=True)
    version=models.CharField(max_length=64,blank=True)    
    def __unicode__(self):  
        return self.value
    class Meta:
        ordering=('value',)

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
    # We can't the name of this is a value in vocab, because it might be user generated '''
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
    numeric=models.BooleanField(default=False)
    def __unicode__(self):
        return self.name
    def copy(self,constraint):
        new=NewParam(name=self.name,constraint=constraint,ptype=self.ptype,controlled=self.controlled,
                      vocab=self.vocab,value=self.value,definition=self.definition,units=self.units,
                      numeric=self.numeric)
        new.save()
    
class DataContainer(models.Model):
    ''' This holds multiple data objects. Some might think of this as a file '''
    # a name for drop down file lists (and yes it's short)
    abbrev=models.CharField(max_length=32)
    # and a real name for disambiguation, although the link is authorative.
    name=models.CharField(max_length=128)
    # a link to the object if possible:
    link=models.URLField(blank=True)
    # what's in the container
    description=models.TextField()
    # container format
    format=models.ForeignKey('Value',blank=True,null=True) 
    # centre that owns this data container
    centre=models.ForeignKey('Centre',blank=True,null=True)
    # references (including web pages)
    reference=models.ForeignKey(Reference,blank=True,null=True)
    def __unicode__(self):
        if self.abbrev <> '':
            return self.abbrev
        else: return self.name[0:31]  # truncation ...
    class Meta:
        ordering=('centre','name')
    
class DataObject(models.Model):
    ''' Holds a variable within a data container '''
    container=models.ForeignKey(DataContainer)
    description=models.TextField()
    # if the data object is a variable within a dataset at the target uri, give the variable
    variable=models.CharField(max_length=128,blank=True)
    # and if possible the CF name
    cfname=models.ForeignKey('Value',blank=True,null=True,related_name='data_cfname')
    # references (including web pages)
    reference=models.ForeignKey(Reference,blank=True,null=True)
    # not using this at the moment, but keep for later: csml/science type
    featureType=models.ForeignKey('Value',blank=True,null=True)
    # not using this at the moment, but keep for later:
    drsAddress=models.CharField(max_length=256,blank=True)
    def __unicode__(self): return self.variable
    class Meta:
        ordering=('variable',)
    
class CouplingGroup(models.Model):
    ''' This class is used to help manage the couplings in terms of presentation and
    their copying between simulations '''
    # parent component, must be a model for CMIP5:
    component=models.ForeignKey(Component)
    # may also be associated with a simulation, in which case there is an original
    simulation=models.ForeignKey(Simulation,blank=True,null=True)
    original=models.ForeignKey('CouplingGroup',blank=True,null=True)
    # to limit the size of drop down lists, we have a list of associated files
    associatedFiles=models.ManyToManyField(DataContainer,blank=True,null=True)
    def duplicate4sim(self,simulation):
        '''Make a copy of self, and associate with a simulation'''
        # first make a copy of self
        args=['component',]
        kw={'original':self,'simulation':simulation}
        for a in args:kw[a]=self.__getattribute__(a)
        new=CouplingGroup(**kw)
        new.save()
        #can't do the many to manager above, need to do them one by one
        for af in self.associatedFiles.all():new.associatedFiles.add(af)
        # now copy all the individual couplings associated with this group
        cset=self.coupling_set.all()
        for c in cset: c.copy(new)
        return new
    def propagateClosures(self):
        ''' This is a one stop shop to update all the closures from an original source
        model coupling group to a simulation coupling group '''
        if self.original is None:raise ValueError('No original coupling group available')
        #start by finding all the couplings in this coupling set.
        myset=self.coupling_set.all()
        for coupling in myset:
            # find all the relevant closures and copy them
            coupling.propagateClosures()          
        return '%s couplings updated '%len(myset)
    class Meta:
        ordering=['component']
    def __unicode__(self):
        return 'Coupling Group for %s (simulation %s)'%(self.component,self.simulation)

class Coupling(models.Model):
    # parent coupling group
    parent=models.ForeignKey(CouplingGroup)
    # coupling for:
    targetInput=models.ForeignKey(ComponentInput)
    # coupling details (common to all closures)
    inputTechnique=models.ForeignKey('Value',related_name='%(class)s_InputTechnique',blank=True,null=True)
    FreqUnits=models.ForeignKey('Value',related_name='%(class)s_FreqUnits',blank=True,null=True)
    couplingFreq=models.IntegerField(blank=True,null=True)
    manipulation=models.TextField(blank=True,null=True)
    # original if I'm a copy.
    original=models.ForeignKey('Coupling',blank=True,null=True)
    def __unicode__(self):
        if self.parent.simulation:
            return 'CouplingFor:%s(in %s)'%(self.targetInput,self.parent.simulation)
        else:
            return 'CouplingFor:%s'%self.targetInput
    def copy(self,group):
        '''Make a copy of self, and associate with a new group'''
        # first make a copy of self
        args=['inputTechnique','couplingFreq','FreqUnits','manipulation','targetInput']
        kw={'original':self,'parent':group}
        for a in args:kw[a]=self.__getattribute__(a)
        new=Coupling(**kw)
        new.save()
        # We don't copy all the individual closures by default. Currently we
        # imagine that can happen in two ways but both are under user control.
        # Either they to it individually, or they do it one by one.
        return new
    def propagateClosures(self):
        ''' Update my closures from an original if it exists '''
        if self.original is None:raise ValueError('No original coupling available')
        for cmodel in [InternalClosure,ExternalClosure]:
            set=cmodel.objects.filter(coupling=self.original)
            for i in set: i.makeNewCopy(self)
        return '%s updated from %s'%(self,self.original)
    class Meta:
        ordering=['targetInput']
    
class CouplingClosure(models.Model):
    ''' Handles a specific closure to a component '''
    # we don't need a closed attribute, since the absence of a target means it's open.
    coupling=models.ForeignKey(Coupling,blank=True,null=True)
    #http://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    spatialRegrid=models.ForeignKey('Value',related_name='%(class)s_SpatialRegrid')
    temporalTransform=models.ForeignKey('Value',related_name='%(class)s_TemporalTransform')
    class Meta:
        abstract=True
   

class InternalClosure(CouplingClosure): 
    target=models.ForeignKey(Component,blank=True,null=True)
    ctype='internal'
    def __unicode__(self):
        return 'iClosure %s'%self.target
    def makeNewCopy(self,coupling):
        ''' Copy closure to a new coupling '''
        kw={'coupling':coupling}
        for key in ['spatialRegrid','temporalTransform','target']:
            kw[key]=self.__getattribute__(key)
        new=self.__class__(**kw)
        new.save()
    
class ExternalClosure(CouplingClosure):
    ''' AKA boundary condition '''
    target=models.ForeignKey(DataObject,blank=True,null=True)
    targetFile=models.ForeignKey(DataContainer,blank=True,null=True)
    ctype='external'
    def __unicode__(self):
        return 'eClosure %s'%self.target    
    def makeNewCopy(self,coupling):
        ''' Copy closure to a new coupling '''
        kw={'coupling':coupling}
        for key in ['spatialRegrid','temporalTransform','target','targetFile']:
            kw[key]=self.__getattribute__(key)
        new=self.__class__(**kw)
        new.save()
        
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
                objects[n-1-i].delete()
            elif ndif < 0:
                e=EnsembleMember(ensemble=self,memberNumber=n+i+1)
                e.save()
    
class EnsembleMember(models.Model):
    ensemble=models.ForeignKey(Ensemble,blank=True,null=True)
    memberNumber=models.IntegerField()
    mod=models.ForeignKey('Modification',blank=True,null=True)
    def __unicode__(self):
        return '%s ensemble member %s'%(self.ensemble.simulation,self.memberNumber)
    class Meta:
        ordering=('memberNumber',)
    
class Conformance(models.Model):
    ''' This relates a numerical requirement to an actual solution in the simulation '''
    # the identifier of the numerical requirement:
    requirement=models.ForeignKey(NumericalRequirement)
    # simulation owning the requirement 
    simulation=models.ForeignKey(Simulation)
    # conformance type from the controlled vocabulary
    ctype=models.ForeignKey(Value,blank=True,null=True)
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
    class Meta:
        ordering=('mnemonic',)
    
class InputMod(Modification):
    ''' Simulation initial condition '''
    # could need a date to override the date in the file for i.c. ensembles.
    date=models.DateField(blank=True,null=True) # watch out, model calendars
    # could be to multiple inputs ... otherwise it'd get untidy
    inputs=models.ManyToManyField(Coupling,blank=True,null=True)
         
class ModelMod(Modification):
    #we could try and get to the parameter values as well ...
    component=models.ForeignKey(Component)
    
class DocFeed(Feed):
    ''' This is the atom feed for xml documents available from the questionnaire '''
    # See http://code.google.com/p/django-atompub/wiki/UserGuide
    feeds={'platform':Platform.objects.all(),
           'simulation':Simulation.objects.all(),
           'component':Component.objects.filter(isModel=True),
           'experiment':Experiment.objects.all()}
    def get_object(self,params):
        ''' Used for parameterised feeds '''
        assert params[0] in self.feeds,'Unknown feed request'
        return params[0]
    def feed_id (self,model):
        return 'http://meta4.ceda.ac.uk/questionnaire/feed/%s'%model
    def feed_title(self,model):
        return 'CMIP5 model %s metadata'%model
    def feed_subtitle(self,model):
        return 'Metafor questionnaire - completed %s documents'%model
    def feed_authors(self,model):
        return [{'name':'The metafor team'}]
    def items(self,model):
        return self.feeds[model].order_by('-updated')
    def item_id(self,item):
        return item.uri
    def item_title(self,item):
        t=item.title
        if len(t):
            return '%s (%s)'%(item.abbrev,item.title)
        else: return item.abbrev
    def item_authors(self,item):
        if item.author is not None:
            return [{'name': item.author.name,'email':item.author.email}]
        else: return []
    def item_updated(self,item):
        return item.updated
    def item_published(self,item):
        return item.created
    def item_summary(self,item):
        if item.description:
            return item.description
        else:
            return '%s'%item
    def item_content(self,item):
        ''' Return out of line link to the content'''
        return {"type": "application/xml", "src": item.urlxml()},""
    
#
# =========================================================================================
#
        

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
        return o
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
        group=CouplingGroup.objects.get(simulation=simulation)
        self.fields['inputs'].queryset=Coupling.objects.filter(parent=group)
        ivocab=Vocab.objects.get(name='InputTypes')
        self.fields['mtype'].queryset=Value.objects.filter(vocab=ivocab)
        
class ConformanceForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"3"}),required=False) 
    # We need the queryset, note that the queryset is limited in the specialisation
    q1,q2=ModelMod.objects.all(),Coupling.objects.all()
    mod=forms.ModelMultipleChoiceField(required=False,queryset=q1,widget=forms.SelectMultiple(attrs={'size':'3'}))
    coupling=forms.ModelMultipleChoiceField(required=False,queryset=q2,widget=forms.SelectMultiple(attrs={'size':'3'}))
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
        print 'BNL',len(groups),simulation,self.fields['coupling'].queryset
        v=Vocab.objects.get(name='ConformanceTypes')
        self.fields['ctype'].queryset=Value.objects.filter(vocab=v)
        self.showMod=len(self.fields['mod'].queryset)
        self.showCoupling=len(self.fields['coupling'].queryset)
       
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
        return s

class ComponentForm(forms.ModelForm):
    #it appears that when we explicitly set the layout for forms, we have to explicitly set 
    #required=False, it doesn't inherit that from the model as it does if we don't handle the display.
    
    #implemented=forms.BooleanField(required=True)
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'class':'inputH1'}))
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
    #link=forms.URLField(widget=forms.TextInput(attrs={'size':'55'}))
    link=refLinkField(widget=forms.TextInput(attrs={'size':'55'}),required=False)
    class Meta:
        model=Reference
        exclude=('centre',)
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='ReferenceTypes')
        self.fields['refType'].queryset=Value.objects.filter(vocab=v)
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
    
class PlatformForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'class':'optin','cols':"80",'rows':"4"}),required=False)
    maxProcessors=forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin','size':5}),required=False)
    coresPerProcessor=forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin','size':5}),required=False)
    class Meta:
        model=Platform
        exclude=('centre','uri','metadataMaintainer')
        
class ComponentInputForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'cols':"120",'rows':"2"}),required=False)
    abbrev=forms.CharField(widget=forms.TextInput(attrs={'size':'24'}))
    units=forms.CharField(widget=forms.TextInput(attrs={'size':'48'}),required=False)
    class Meta:
        model=ComponentInput
        exclude=('owner','realm') # we know these
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='InputTypes')
        self.fields['ctype'].queryset=Value.objects.filter(vocab=v)
    
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
        if data == u'': data=str(uuid.uuid1())
        return data
    def save(self):
        r=forms.ModelForm.save(self,commit=False)
        r.centre=self.hostCentre
        r.save()
        return r
        
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
    
class DataContainerForm(forms.ModelForm):
    ''' This is the form used to edit "files" ... '''
    name=forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
    link=forms.URLField(widget=forms.TextInput(attrs={'size':'45'}),required=False)
    description=forms.CharField(widget=forms.Textarea({'cols':'50','rows':'4'}),required=False)
    class Meta:
        model=DataContainer
        exclude=('centre','dataObject')
    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        v=Vocab.objects.get(name='FileFormats')
        self.fields['format'].queryset=Value.objects.filter(vocab=v)
        self.hostCentre=None
    def specialise(self,centre):
        self.fields['reference'].queryset=Reference.objects.filter(centre=centre)|Reference.objects.filter(centre=None)
    def save(self):
        ''' Need to add the centre, and save the subform too '''
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        o.save()
        return o
    def clean(self):
        ''' Needed to ensure name uniqueness within a centre, and handle the subform '''
        return uniqueness(self,self.hostCentre,'name')

class DataObjectForm(forms.ModelForm):
    description=forms.CharField(widget=forms.Textarea({'cols':'50','rows':'2'}),required=False)
    variable=forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
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
            qset=DataObject.objects.filter(variable=None) # should get an empty set
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
    
    
    
