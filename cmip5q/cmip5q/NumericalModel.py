
# This file has the NumericalModel class, which is independent of the django views (but not
# the django strage), used to instantiate numerical models from xml versions of the mindmaps,
# and to produce xml instances of the django storage ...

from protoq.models import *
from XMLinitialiseQ import realms

from xml.etree import ElementTree as ET
import uuid
import logging
import unittest
import os

class NumericalModel:
    
    ''' Handles the creation of a model instance in the database, either from XML storage
    or from a pre-existing instance '''
    
    def __init__(self,id,centre=None):
        ''' Initialise from storage, or build a new one '''
        if id==0:
            if centre is None:
                raise ValueError('Need valid centre to create a new model')
            else:
                self.component=self.makeEmptyModel(centre)
        else:
            self.component=Component.objects.get(pk=id)
        
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
        return component
        
    def read(self):
       
        ''' Read mindmap XML documents to build a complete model description '''
            
        mindMapDir = os.path.join(os.path.dirname(__file__), 
                            'data',
                            'mindmaps')
                                
        logging.debug('Looking for mindmaps in %s'%mindMapDir)
        mindmaps=[os.path.join(mindMapDir, f) for f in os.listdir(mindMapDir)
                    if f.endswith('.xml')]
                    
        for m in mindmaps:
            x=XMLVocabReader(m, self.component)
            x.doParse()
            self.component.components.add(x.component)
            logging.debug('Mindmap %s added with component id %s'%(m,x.component.id))
        
        self.component.save()
        logging.info('Created new Model %s'%self.component.id)
        
    def copy(self,original):
        ''' Construct a new model by copying a pre-existing model description '''
        
        logging.debug('Deep model copying not implemented')
        # would have be pretty careful to do all the internal reference copying ...
        
        pass
    
    def export(self,recurse=True):
        ''' Return an XML view of self '''

        logging.debug('NumericalModel:export returning an xml document')
        root=ET.Element('CIMRecord',{'documentVersion': '1.2'})
        ET.SubElement(root,'id').text='[TBD]'
        self.exportAddComponent(root,self.component,recurse)
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
            raise ValueError(
            'Cannot unittest NumericalModel without a centre already saved in django database')
        self.model=NumericalModel(0,self.centre)
       
    def testReadFromXML(self):
        self.model.read()
        
        c=self.model.component
        self.assertEqual(c.scienceType,'model')
        self.assertEqual(True,c.isModel)
        self.assertEqual(False,c.isRealm)
        
        for c in self.model.component.components.values_list():
            self.assertEqual(True,c.scienceType in realms)
            self.assertEqual(True,c.isRealm)
            self.assertEqual(False,c.isModel)
            
                                
                                
