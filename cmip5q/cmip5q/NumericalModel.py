
# This file has the NumericalModel class, which is independent of the django views (but not
# the django strage), used to instantiate numerical models from xml versions of the mindmaps,
# and to produce xml instances of the django storage.

from protoq.models import *
from XMLinitialiseQ import realms

from xml.etree import ElementTree as ET
import uuid
import logging
import unittest
import os


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
    
    def __init__(self,centre,id=0,xml=False):
        ''' Initialise by copy from django storage, or build a new one from the XML '''
        
        klass=centre.__class__
        if klass != Centre:
            raise ValueError('Need a valid django centre class for NumericalModel, got %s'%klass)
        self.centre=centre
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
                      authorName='Joe Bloggs',
                      authorEmail='joe@foo.bar',
                      title='GCM Template',
                      abbrev='GCM Template'):
   
        u=str(uuid.uuid1())
        component=Component(scienceType='model',centre=centre,abbrev='',uri=u)
        component.isModel=True
        component.isRealm=False
        component.contact=authorName
        component.email=authorEmail
        component.title=title
        component.abbrev=abbrev
        component.save()
        component.model=component
        component.save()
        self.top=component
        logging.debug('Created empty top level model %s'%component)
        
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
        root=ET.Element('CIMRecord',{'documentVersion': '1.2'})
        ET.SubElement(root,'id').text='[TBD]'
        self.exportAddComponent(root,self.top,recurse)
        return root

    def exportAddComponent(self,root,c,recurse=True):
        comp=ET.SubElement(root,'modelComponent',{'documentVersion': '[TBD]'})
        '''composition'''
        if recurse:
            '''childComponent'''
            for child in c.components.all():
                comp2=ET.SubElement(comp,'childComponent')
                self.exportAddComponent(comp2,child)
        '''parentComponent'''
        '''deployment'''
        '''shortName'''
        ET.SubElement(comp,'shortName').text=c.abbrev
        '''longName'''
        ET.SubElement(comp,'longName').text=c.title
        '''description'''
        ET.SubElement(comp,'description').text='[TBD]'
        '''license'''
        '''componentProperties'''
        componentProperties=ET.SubElement(comp,'componentProperties')
        pset=Param.objects.filter(component=c)
        for p in pset:
            componentProperty=ET.SubElement(componentProperties,'componentProperty',{'represented':'[TBD]'})
            '''shortName'''
            ET.SubElement(componentProperty,'shortName').text=p.name
            '''longName'''
            ET.SubElement(componentProperty,'longName').text='[TBD]'
            '''description'''
            '''type'''
            ET.SubElement(componentProperty,'type').text='[TBD]'
            '''value'''
            ET.SubElement(componentProperty,'value').text=p.value
            #ET.SubElement(componentProperty,'ptype').text=p.ptype
            #ET.SubElement(componentProperty,'vocab').text=p.vocab
        '''numericalProperties'''
        ET.SubElement(comp,'numericalProperties')
        '''scientificProperties'''
        ET.SubElement(comp,'scientificProperties')
        '''grid'''
        '''responsibleParty'''
        resp=ET.SubElement(comp,'responsibleParty') #type gmd:xxxx
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        name=ET.SubElement(resp,'gmd:individualName')
        ET.SubElement(name,'gco:CharacterString').text=c.contact
        # </gmd:individualName/>
        # <gmd:organisationName/>
        # <gmd:positionName/>
        # <gmd:contactInfo>
        contact=ET.SubElement(resp,'gmd:contactInfo')
        #     <gmd:phone/>
        #     <gmd:address>
        address=ET.SubElement(contact,'gmd:address')
        #         <gmd:deliveryPoint/>
        #         <gmd:city/>
        #         <gmd:administrativeArea/>
        #         <gmd:postalCode/>
        #         <gmd:country/>
        #         <gmd:electronicMailAddress>
        email=ET.SubElement(address,'gmd:electronicMailAddress')
        ET.SubElement(email,'gco:CharacterString').text=c.email
        #         </gmd:electronicMailAddress>
        #     </gmd:address>
        #     <gmd:onlineResource/>
        #     <gmd:hoursOfService/>
        #     <gmd:contactInstructions/>
        # </gmd:contactInfo>
        # <gmd:roll/>

        '''activity'''
        '''type'''
        ET.SubElement(comp,'type').text=c.scienceType
        '''timing'''
        ET.SubElement(comp,'timing').text='[TBD]'
        '''documentID'''
        ET.SubElement(comp,'documentID').text='[TBD]'
        '''documentAuthor'''
        '''documentCreationDate'''
        ET.SubElement(comp,'documentCreationDate').text='[TBD]'
        #e.text=datetime.date
        '''documentGenealogy'''
        '''quality'''
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
        logging.debug("Instantiated Parser for %s"% item.tag)
        if item.attrib['name']:
            logging.debug("name = %s"%item.attrib['name'])
        else:
            logging.debug("[no name]")

    def __handleParam(self,elem):
        ''' Handle parameters and add their properties to parent component '''
        paramName=elem.attrib['name']
        choiceType=elem.attrib['choice']
        logging.debug('For %s found parameter %s with choice %s'%(self.item.attrib['name'],paramName,choiceType))
        if choiceType in ['OR','XOR']:
            #create and load vocabulary
            v=Vocab(uri=str(uuid.uuid1()),name=paramName+'Vocab')
            v.save()
            logging.debug('Created vocab %s'%v.name)
            for item in elem:
                if item.tag=='value':
                    value=Value(vocab=v,value=item.attrib['name'])
                    value.save()
                    logging.debug('Added %s to vocab %s'%(value.value,v.name))
                else:
                    logging.info('Found unexpected tag %s in %s'%(item.tag,paramName))
            p=Param(name=paramName,component=self.component,ptype=choiceType,vocab=v)
            p.save()
            logging.info('Added parameter %s to component %s (%s)'%(paramName,self.component.abbrev,self.component.id))
               
    def add(self, doSubs, realm=None):
        u=str(uuid.uuid1())
        component = Component(
                title='',
                scienceType=self.item.attrib['name'],
                abbrev=self.item.attrib['name'],
                uri=u,
                centre=self.model.centre,
                contact=self.model.contact,
                email=self.model.email)
        component.save() # we need a primary key value so we can add subcomponents later
        self.component=component # used to assign parameters ...
        
        logging.debug('Handling Component %s (%s)'%(component.abbrev,component.scienceType))
        if component.scienceType in realms:
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
            for subchild in self.item:
                if subchild.tag == "component":
                    logging.debug("Found child : %s"%subchild.tag)
                    subComponentParser = ComponentParser(subchild, self.model)
                    # Handle child components of this one (True = recursive)
                    child=subComponentParser.add(True,realm=realm)
                    logging.debug("Adding sub-component %s to component %s (model %s, realm %s)"%(child.abbrev, component.abbrev,child.model,child.realm))
                    component.components.add(child)
                elif subchild.tag == 'parameter': 
                    self.__handleParam(subchild)
   	
        component.save()
        return component
                
class TestFunctions(unittest.TestCase):
    ''' We can have real unittests for this, because it's independent of the webserver '''
    def setUp(self):
        try:
            self.centre=Centre.objects.get(pk=1)
        except: 
            u=str(uuid.uuid1())
            c=Centre(abbrev='CMIP5',title='Dummy testing version',
                     uri=u)
            logging.debug('Created dummy centre for testing')
            c.save()
            self.centre=c 
       
    def NOtest0ReadFromXML(self):
        
        nm=NumericalModel(self.centre,xml=True)
        
        c=nm.top
        self.assertEqual(c.scienceType,'model')
        self.assertEqual(True,c.isModel)
        self.assertEqual(False,c.isRealm)
        
        for c in nm.top.components.all():
            self.assertEqual(True,c.scienceType in realms)
            self.assertEqual(True,c.isRealm)
            self.assertEqual(False,c.isModel)
        
        self.nm=nm
            
    def test1CopyModel(self):
        
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
                                
                                
