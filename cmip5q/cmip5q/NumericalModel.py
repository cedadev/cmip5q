
# This file has the NumericalModel class, which is independent of the django views (but not
# the django strage), used to instantiate numerical models from xml versions of the mindmaps,
# and to produce xml instances of the django storage.

from protoq.models import *
from XMLinitialiseQ import VocabList

# move from ElementTree to lxml.etree
#from xml.etree import ElementTree as ET
from lxml import etree as ET
import uuid
import logging
import unittest
import os
import datetime

Realms=VocabList['Realms']

def initialiseModel():
    ''' Setup a template for model copying in the dummy CMIP5 centre '''
    try:
        c=Centre.objects.get(abbrev='CMIP5')
    except:
        cl=Centre.objects.all()
        logging.debug('Unable to read dummy CMIP5 centre description, existing centres are %s'%cl)
        return False
    m=NumericalModel(c,xml=True)
    return True

class NumericalModel:
    
    ''' Handles the creation of a model instance in the database, either from XML storage
    or from a pre-existing instance '''
    
    CIM_NAMESPACE = "http://www.metaforclimate.eu/cim/1.1"
    SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_INSTANCE_NAMESPACE_BRACKETS = "{"+SCHEMA_INSTANCE_NAMESPACE+"}"
    CIM_URL = "cim.xsd"
    GMD_NAMESPACE = "http://www.isotc211.org/2005/gmd"
    GMD_NAMESPACE_BRACKETS="{"+GMD_NAMESPACE+"}"
    GCO_NAMESPACE = "http://www.isotc211.org/2005/gco"
    GCO_NAMESPACE_BRACKETS="{"+GCO_NAMESPACE+"}"

    def __init__(self,centre,id=0,xml=False):
        ''' Initialise by copy from django storage, or build a new one from the XML '''
        
        klass=centre.__class__
        if klass != Centre:
            raise ValueError('Need a valid django centre class for NumericalModel, got %s'%klass)
        self.centre=centre
        self.joe=ResponsibleParty.objects.filter(centre=centre).get(name='Unknown')
        
        if id==0: xml=True
        if xml and id<>0:
            raise ValueError('Incompatible arguments to numerical model')
        if id<>0:
            self.top=Component.objects.get(id=id)
        elif xml:
            self.makeEmptyModel(centre)
            self.read()
        else:
            raise ValueError('Nothing to do in NumericalModel')
        
        
    def copy(self):
        
        new=self.top.makeNewCopy(self.centre)
        logging.debug('Made new model %s with id %s in %s'%(new,new.id,self.centre))
        return new
    
    def makeEmptyModel(self,
                      centre,
                      author=None,
                      contact=None,
                      funder=None,
                      title='GCM Template',
                      abbrev='GCM Template'):
        
        if author is None: author=self.joe
        if funder is None: funder=self.joe
        if contact is None: contact=self.joe
        
        component=Component(scienceType='model',centre=centre,abbrev='',uri=str(uuid.uuid1()),
                            author=author,contact=contact,funder=funder)
        component.isModel=True
        component.isRealm=False
        component.title=title
        component.abbrev=abbrev
        component.save()
        component.model=component
        component.controlled=True
        component.save()
        self.top=component
        logging.debug('Created empty top level model %s'%component)
        # now get a placeholder paramgroup and constraint group
        p=ParamGroup(component=component)
        p.save() 
        cg=ConstraintGroup(constraint='',parentGroup=p)
        cg.save()
        
    def read(self):
       
        ''' Read mindmap XML documents to build a complete model description '''
            
        mindMapDir = os.path.join(os.path.dirname(__file__), 
                            'data',
                            'mindmaps')
                                
        logging.debug('Looking for mindmaps in %s'%mindMapDir)
        mindmaps=[os.path.join(mindMapDir, f) for f in os.listdir(mindMapDir)
                    if f.endswith('.xml')]
                    
        for m in mindmaps:
            x=XMLVocabReader(m, self.top)
            x.doParse()
            self.top.components.add(x.component)
            logging.debug('Mindmap %s added with component id %s'%(m,x.component.id))
        
        self.top.save()
        logging.info('Created new Model %s'%self.top.id)
    
    def export(self,recurse=True):
        ''' Return an XML view of self '''

        logging.debug('NumericalModel:export returning an xml document')
        NSMAP = {None  : self.CIM_NAMESPACE,             \
                 "xsi" : self.SCHEMA_INSTANCE_NAMESPACE, \
                 "gmd" : self.GMD_NAMESPACE,             \
                 "gco" : self.GCO_NAMESPACE}
        root=ET.Element('CIMRecord', \
                        attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                        nsmap=NSMAP)
        ET.SubElement(root,'id').text='[TBD1]'
        self.exportAddComponent(root,self.top,1,recurse)
        return root

    def exportAddComponent(self,root,c,nest,recurse=True):

      if c.implemented:
        if nest==1:
          comp=ET.SubElement(root,'modelComponent',{'documentVersion': '-1'}) # TBD2
        else:
          comp=ET.SubElement(root,'modelComponent')
        '''composition'''
        if recurse:
            '''childComponent'''
            for child in c.components.all():
              if child.implemented:
                comp2=ET.SubElement(comp,'childComponent')
                self.exportAddComponent(comp2,child,nest+1)
        '''parentComponent'''
        '''deployment'''
        '''shortName'''
        ET.SubElement(comp,'shortName').text=c.abbrev
        '''longName'''
        ET.SubElement(comp,'longName').text=c.title
        '''description'''
        ET.SubElement(comp,'description').text=c.description
        '''license'''
        '''componentProperties'''
        componentProperties=ET.SubElement(comp,'componentProperties')
        pgset=ParamGroup.objects.filter(component=c)
        for pg in pgset:
            componentProperty=ET.SubElement(componentProperties,'componentProperty',{'represented':'false'}) # [TBD3]
            '''shortName'''
            ET.SubElement(componentProperty,'shortName').text=pg.name
            '''longName'''
            ET.SubElement(componentProperty,'longName').text=pg.name

            # the internal questionnaire representation is that all parameters
            # are contained in a constraint group
            constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
            for con in constraintSet:
                pset=NewParam.objects.filter(constraint=con)
                for p in pset:
                    property=ET.SubElement(componentProperty,'componentProperty')
                    '''shortName'''
                    ET.SubElement(property,'shortName').text=p.name
                    '''longName'''
                    ET.SubElement(property,'longName').text=p.name
                    '''description'''
                    '''type'''
                    ET.SubElement(property,'type',{"value":"other"}) # TBD4
                    '''value'''
                    ET.SubElement(property,'value').text=p.value
                    #ET.SubElement(property,'ptype').text=p.ptype
                    #ET.SubElement(property,'vocab').text=p.vocab
        '''numericalProperties'''
        ET.SubElement(comp,'numericalProperties')
        '''scientificProperties'''
        ET.SubElement(comp,'scientificProperties')
        '''grid'''
        '''responsibleParty'''
        resp=ET.SubElement(comp,'responsibleParty') #type gmd:xxxx
        ciresp=ET.SubElement(resp,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        #name=ET.SubElement(resp,'gmd:individualName')
        #ET.SubElement(name,'gco:CharacterString').text=c.contact
        name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
        ###ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=c.contact
        # </gmd:individualName/>
        # <gmd:organisationName/>
        # <gmd:positionName/>
        # <gmd:contactInfo>
        #contact=ET.SubElement(ciresp,'gmd:contactInfo')
        contact=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'contactInfo')
        cicontact=ET.SubElement(contact,self.GMD_NAMESPACE_BRACKETS+'CI_Contact')
        #     <gmd:phone/>
        #     <gmd:address>
        #address=ET.SubElement(cicontact,'gmd:address')
        address=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'address')
        ciaddress=ET.SubElement(address,self.GMD_NAMESPACE_BRACKETS+'CI_Address')
        #         <gmd:deliveryPoint/>
        #         <gmd:city/>
        #         <gmd:administrativeArea/>
        #         <gmd:postalCode/>
        #         <gmd:country/>
        #         <gmd:electronicMailAddress>
        #email=ET.SubElement(ciaddress,'gmd:electronicMailAddress')
        #ET.SubElement(email,'gco:CharacterString').text=c.email
        email=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'electronicMailAddress')
        ###ET.SubElement(email,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=c.email
        #         </gmd:electronicMailAddress>
        #     </gmd:address>
        #     <gmd:onlineResource/>
        #     <gmd:hoursOfService/>
        #     <gmd:contactInstructions/>
        # </gmd:contactInfo>
        # <gmd:roll/>
        role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')#empty

        '''activity'''
        '''type'''
        comp.append(ET.Comment("value attribute in element type should have value "+c.scienceType+" but this fails the cim validation at the moment"))
        ET.SubElement(comp,'type',{'value':'other'}) # c.scienceType
        #ET.SubElement(comp,'type').text=c.scienceType
        '''timing'''
        comp.append(ET.Comment("Made up values for timing in order pass cim validation"))
        timing=ET.SubElement(comp,'timing',{'units':'seconds'})
        ET.SubElement(timing,'rate').text='1'
        if nest==1:
          '''documentID'''
          ET.SubElement(comp,'documentID').text='[TBD6]'
          '''documentAuthor'''
          #ET.SubElement(comp,'documentAuthor').text=c.contact
          ET.SubElement(comp,'documentAuthor')
          '''documentCreationDate'''
          #ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())
          ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
        '''documentGenealogy'''
        '''quality'''
      else:
        logging.debug("component "+c.abbrev+" has implemented set to false")
      return

class XMLVocabReader:
    # original author, Matt Pritchard
    ''' Reads XML vocab structure. '''
    def __init__(self,filename, model):
        ''' Initialise from mindmap file '''
        self.etree=ET.parse(filename)
        self.root=self.etree.getroot() # should be the "vocab" element
        self.model=model
            
    def doParse(self):
        first = self.root.findall('component')[0]
        logging.info("New component: %s for model %s"%(first.attrib['name'],self.model))
        # Initiate new top-level component in django:
        modelParser = ComponentParser(first, self.model)
        self.component=modelParser.add(True)
		
class ComponentParser:
    ''' class for handling all elements '''
    def __init__(self, item, model):
        ''' initialise  parser '''
        self.item = item
        self.model = model
        #logging.debug("Instantiated Parser for %s"% item.tag)
        if item.attrib['name']:
            logging.debug("name = %s"%item.attrib['name'])
        else:
            logging.debug("[no name]")
            
    def __handleParamGrp(self,elem):
        ''' Handle the parameter groups consisting of parameters and constraints '''
        p=ParamGroup(name=elem.attrib['name'],component=self.component)
        p.save()
        cg=None
        empty=True
        for item in elem:
            empty=False
            if item.tag=='constraint':
                self.__handleConstraint(item,p)
            elif item.tag=='parameter':
                cg=self.__handleNewParam(item,p,cg)
        if empty:
            #create an empty constraint group so new parameters can be added.
            cg=ConstraintGroup(constraint='',parentGroup=p)
            cg.save()
            
    def __handleConstraint(self,elem,pg):
        ''' Handle Constraints'''
        c=ConstraintGroup(constraint=elem.attrib['name'],parentGroup=pg)
        c.save()
        for item in elem:
            self.__handleNewParam(item,pg,c)
    
    def __handleKeyboardValue(self,elem):
        ''' Parse for and handle values from the keyboard, e.g.
        <value format="string" name="list of 2D species emitted"/>
        <value format="numerical" name="lat_min" units="degN"/>'''
        # currently ignoring the value names ...
        velem=elem.find('value')
        if velem is None:
            logging.info('ERROR: Unable to parse %s(%s)'%(elem.tag,elem.text))
            return False,None
        keys=velem.attrib.keys()
        numeric,units=False,None
        if 'format' in keys: 
            if velem.attrib['format']=='numerical': numeric=True
        if 'units' in keys: units=velem.attrib['units']
        return numeric,units
    
    def __handleNewParam(self,elem,pg,cg):
        ''' Add new parameter to cg, if cg none, create one in pg '''
        if cg is None:
            cg=ConstraintGroup(constraint='',parentGroup=pg)
            cg.save()
        paramName=elem.attrib['name']
        choiceType=elem.attrib['choice']
        logging.debug('For %s found parameter %s with choice %s'%(self.item.attrib['name'],paramName,choiceType))
       
        if choiceType in ['OR','XOR']:
            #create and load vocabulary
            v=Vocab(uri=str(uuid.uuid1()),name=paramName+'Vocab')
            v.save()
            logging.debug('Created vocab %s'%v.name)
            co,info=None,None
            for item in elem:
                if item.tag=='value':
                    value=Value(vocab=v,value=item.attrib['name'])
                    value.save()
                elif item.tag=='definition':
                    defn=item.text
                else:
                    logging.info('Found unexpected tag %s in %s'%(item.tag,paramName))
            p=NewParam(name=paramName,constraint=cg,ptype=choiceType,vocab=v,definition=defn)
            p.save()
        elif choiceType in ['keyboard']:
            defn,units='',''
            delem=elem.find('definition')
            if delem is not None: defn=delem.text
            numeric,units=self.__handleKeyboardValue(elem)
            p=NewParam(name=paramName,constraint=cg,ptype=choiceType,definition=defn,units=units,
                       numeric=numeric)
            p.save()
        elif choiceType in ['couple']:
            # we create an input requirement here and now ...
            ci=ComponentInput(owner=self.component,abbrev=paramName,
                              description='Required by controlled vocabulary for %s'%self.component,
                              realm=self.component.realm)
            ci.save()
            #and we have to create a coupling for it too
            cp=Coupling(component=self.component.model,targetInput=ci)
            cp.save()
        else:
            logging.info('ERROR: Ignoring parameter %s'%paramName)
            return
        logging.info('Added component input %s for %s in %s'%(paramName,cg,pg))
        return cg
               
    def add(self, doSubs, realm=None):
        u=str(uuid.uuid1())
        component = Component(
                title='',
                scienceType=self.item.attrib['name'],
                abbrev=self.item.attrib['name'],
                controlled=True,
                uri=u,
                centre=self.model.centre,
                contact=self.model.contact,
                author=self.model.author,
                funder=self.model.funder)
        component.save() # we need a primary key value so we can add subcomponents later
        self.component=component # used to assign parameters ...
        
        logging.debug('Handling Component %s (%s)'%(component.abbrev,component.scienceType))
        if component.scienceType in Realms:
            realm=component
            component.model=self.model
            component.isRealm=True
            component.realm=component
        else:
            component.model=self.model
            # if realm doesn't exist, then somehow we've broken our controlled vocab
            # realm relationship.
            component.realm=realm
            
        if doSubs:
            #temporary
            for subchild in self.item:
                if subchild.tag == "component":
                    #logging.debug("Found child : %s"%subchild.tag)
                    subComponentParser = ComponentParser(subchild, self.model)
                    # Handle child components of this one (True = recursive)
                    child=subComponentParser.add(True,realm=realm)
                    logging.debug("Adding sub-component %s to component %s (model %s, realm %s)"%(child.abbrev, component.abbrev,child.model,child.realm))
                    component.components.add(child)
                elif subchild.tag == 'parametergroup': 
                    self.__handleParamGrp(subchild)
                elif subchild.tag == 'parameter':
                    print logging.info('OOOOOOOPPPPPPs')
                    self.__handleParam(subchild)
                else:
                    logging.debug('Ignoring tag %s for %s'%(subchild.tag,self.component))
   	
        component.save()
        return component
                
class TestFunctions(unittest.TestCase):
    ''' We can have real unittests for this, because it's independent of the webserver '''
    def setUp(self):
        try:
            self.centre=Centre.objects.get(abbrev="CMIP5")
        except: 
            u=str(uuid.uuid1())
            c=Centre(abbrev='CMIP5',name='Dummy testing version',
                     uri=u)
            logging.debug('Created dummy centre for testing')
            c.save()
            self.centre=c 
       
    def test0ReadFromXML(self):
        
        nm=NumericalModel(self.centre,xml=True)
        
        c=nm.top
        self.assertEqual(c.scienceType,'model')
        self.assertEqual(True,c.isModel)
        self.assertEqual(False,c.isRealm)
        
        for c in nm.top.components.all():
            self.assertEqual(True,c.scienceType in Realms)
            self.assertEqual(True,c.isRealm)
            self.assertEqual(False,c.isModel)
        
        self.nm=nm
            
    def NOtest1CopyModel(self):
        
        model=Component.objects.filter(abbrev='GCM Template')[0]
        logging.info('Test 1 using component %s'%model.id)
        nm=NumericalModel(self.centre,id=model.id)
        
        model=nm.top
        copy=nm.copy()
         
        self.assertEqual(str(model.title),str(copy.title))
        self.assertEqual(str(model.model),str(copy.model))
            
        originalRealms=model.components.all()
        copyRealms=copy.components.all()
        
        for i in range(len(originalRealms)):
            self.assertEqual(str(originalRealms[i].abbrev),str(copyRealms[i].abbrev))
        
