from protoq.models import *
from xml.etree import ElementTree as ET
import uuid
import logging

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
        v=Vocab.objects.get(name='conformanceTypes')
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

class NumericalExperiment:
    ''' Handles the reading of a numerical experiment, and the insertion into the django db '''
    
    def __init__(self,filename):
        ''' Reads CIM V1.0 format numerical experiments '''
        self.etree=ET.parse(filename)
        logging.debug('Parsing filename %s'%filename)
	self.root=self.etree.getroot() 
        
        self.rationale=getText(self.root,'rationale')
        self.why=getText(self.root,'Why')
        
        self.numericalRequirements=[]
        
        for r in self.root.findall('{%s}numericalRequirement'%cimv):
            n=numericalRequirement(r)
            if n.id<>'':self.numericalRequirements.append(n)
            
        (s,e)=('{%s}requiredDuration/{%s}startDate'%(cimv,cimv),
                '{%s}requiredDuration/{%s}endDate'%(cimv,cimv))
                
        self.duration=[getText2(self.root,i) for i in (s,e)]
                      
        self.docID=(self.root.find('{%s}documentID'%cimv).text or 'No ID Found')
        self.shortName=getText(self.root,'shortName')
        self.longName=getText(self.root,'longName')
        logging.debug(
           'Experiment %s has %s requirements'%(self.shortName,len(self.numericalRequirements)))
   
    def load(self):
        ''' Loads information into the django database '''
        
        E=Experiment(rationale=self.rationale,
                     why=self.why,
                     docID=self.docID,
                     shortName=self.shortName,
                     startDate=self.duration[0],
                     endDate=self.duration[1])
        if self.longName is not None: E.longName=self.longName
        
        E.save()   # we need to do this before we can have a manytomany field instance
        
        #Do all the numerical requirements.
        # FIXME, assume that they're all independent and no xlinks.
        
        for r in self.numericalRequirements:
            print r.id,r.description
            rid=r.load()
            E.requirements.add(rid)
        
        E.save()
       
        return E.id

if __name__=="__main__":
    import sys
    logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(message)s',)
    filename=sys.argv[1]
    x=NumericalExperiment(filename)
        
        
            
        