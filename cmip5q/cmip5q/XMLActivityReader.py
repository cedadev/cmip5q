from protoq.models import *
from xml.etree import ElementTree as ET
import uuid
import logging
import unittest

cimv='http://www.metaforclimate.eu/cim/1.1'
typekey='{http://www.w3.org/2001/XMLSchema-instance}type'

def getText(elem,path):
    ''' Return text from an element ... if it exists '''
    e=elem.find('{%s}%s'%(cimv,path))
    if e is None: 
        return ''
    else:
        return (e.text or '')
def getText2(elem,path):
    e=elem.find(path)
    if e is None: 
        return '' 
    else: return e.text or ''
    
class numericalRequirement:
    def __init__(self,elem):
        self.description=getText(elem,'description')
        self.id=getText(elem,'id')
        self.name=getText(elem,'name')
        
        if typekey in elem.attrib.keys():
            ctype=elem.attrib[typekey]
        else: ctype=''
        v=Vocab.objects.get(name='NumReqTypes')
        ctypeVals=Value.objects.filter(vocab=v)
        try:
            self.ctype=ctypeVals.get(value=ctype)
        except:
            logging.debug('Invalid numerical requirement type (%s) in %s,%s'%(ctype,self.name,self.id))
            self.ctype=None
       
        if not self.name or self.name=='':
            logging.debug('Numerical Requirement %s [%s,%s]'%(self.id,self.description,self.ctype))
        # FIXME assumes no xlinks

    def load(self):
        ''' Load into django database '''
        n=NumericalRequirement(description=self.description,
                               name=self.name,
                               ctype=self.ctype)
        n.save()
        return n.id

class Duration(object):
    def __init__(self,elem):
        if elem is None:
            self.start,self.end,self.lengthYears=None,None,None
        else:
            self.start=getText(elem,'startDate')
            self.end=getText(elem,'endDate')
            self.length=getText(elem,'lengthYears')
            if self.length=='': self.length=None
        
def calendar(elem):
    cvalues=Value.objects.filter(vocab=Vocab.objects.get(name='CalendarTypes'))
    cnames=[str(i) for i in cvalues]
    if elem:
        cc=elem[0].tag.split('}')[1]
        if cc in cnames:
            return cvalues.get(value=cc)
        else:
            logging.info('Did not find calendar type '+cc) 
    else:
        logging.debug('Could not find calendar')
    return None

class NumericalExperiment(object):
    ''' Handles the reading of a numerical experiment, and the insertion into the django db '''
    
    def __init__(self,filename):
        ''' Reads CIM format numerical experiments '''
        
        self.etree=ET.parse(filename)
        logging.debug('Parsing experiment filename %s'%filename)
	
        self.root=self.etree.getroot() 
        
        for element in ['rationale','description','shortName','longName']:
            self.__setattr__(element,getText(self.root,element))
        
        self.numericalRequirements=[]
        for r in self.root.findall('{%s}numericalRequirement'%cimv):
            n=numericalRequirement(r)
            if n.id<>'':self.numericalRequirements.append(n)
            
        self.duration=Duration(self.root.find('{%s}requiredDuration'%cimv))
        self.calendar=calendar(self.root.find('{%s}calendar'%cimv))
        self.docID=(self.root.find('{%s}documentID'%cimv).text or 'No ID Found')

        
    def load(self):
        ''' Loads information into the django database '''
        
        E=Experiment(rationale=self.rationale,
                     description=self.description,
                     docID=self.docID,
                     shortName=self.shortName,
                     startDate=self.duration.start,
                     endDate=self.duration.end,
                     length=self.duration.length,
                     longName=self.longName,
                     calendar=self.calendar,
                     )     
        E.save()   # we need to do this before we can have a manytomany field instance
        
        #Do all the numerical requirements.
        # FIXME, assume that they're all independent and no xlinks.
        
        for r in self.numericalRequirements:
            rid=r.load()
            E.requirements.add(rid) 
        E.save()
        return E.id
        
class TestFunctions(unittest.TestCase): 
    def testExperiment(self):
        d='data/experiments/'
        filename='6.7b_Aquaplanet_4CO2.xml'
        x=NumericalExperiment(d+filename)
        
            
        