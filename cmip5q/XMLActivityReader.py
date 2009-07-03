from protoq.models import *
from xml.etree import ElementTree as ET
import uuid
import logging

cimv='http://www.metaforclimate.eu/cim/1.1'
typekey='{http://www.w3.org/2001/XMLSchema-instance}type'

class numericalRequirement:
    def __init__(self,elem):
        self.description=(elem.find('{%s}description'%cimv).text or '')
        self.id=(elem.find('{%s}id'%cimv).text or '')
        
        if typekey in elem.attrib.keys():
            self.type=elem.attrib[typekey]
        else: self.type=''
       
        if not self.id or self.id=='':
            logging.debug('Numerical Requirement %s [%s,%s]'%(self.id,self.description,self.type))
        # FIXME assumes no xlinks

    def load(self):
        ''' Load into django database '''
        n=NumericalRequirement(description=self.description,
                               name=self.id,
                               type=self.type)
        n.save()
        return n.id

class NumericalExperiment:
    ''' Handles the reading of a numerical experiment, and the insertion into the django db '''
    
    def __init__(self,filename):
        ''' Reads CIM V1.0 format numerical experiments '''
        self.etree=ET.parse(filename)
	self.root=self.etree.getroot() 
        
        self.rationale=(self.root.find('{%s}rationale'%cimv).text or '')
        self.why=(self.root.find('{%s}Why'%cimv).text or '')
        
        self.numericalRequirements=[]
        
        for r in self.root.findall('{%s}numericalRequirement'%cimv):
            n=numericalRequirement(r)
            if n.id<>'':self.numericalRequirements.append(n)
            
        (s,e)=('{%s}requiredDuration/{%s}startDate'%(cimv,cimv),
                '{%s}requiredDuration/{%s}endDate'%(cimv,cimv))
                
        self.duration=(self.root.find(s).text,self.root.find(e).text)
                      
        self.docID=self.root.find('{%s}documentID'%cimv).text
        logging.debug('Experiment %s has %s requirements'%(self.docID,len(self.numericalRequirements)))
   
    def load(self):
        ''' Loads information into the django database '''
        
        E=Experiment(rationale=self.rationale,
                     why=self.why,
                     docID=self.docID,
                     startDate=self.duration[0],
                     endDate=self.duration[1])
        
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
        
        
            
        