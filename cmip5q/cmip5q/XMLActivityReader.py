from protoq.models import *
from xml.etree import ElementTree as ET
import uuid
import logging
import unittest

cimv='http://www.metaforclimate.eu/cim/1.1'
gmd='http://www.isotc211.org/2005/gmd'
gco="http://www.isotc211.org/2005/gco"
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
    
def numericalRequirement (elem):
    description=getText(elem,'description')
    id=getText(elem,'id')
    name=getText(elem,'name')
    
    if typekey in elem.attrib.keys():
        ctype=elem.attrib[typekey]
    else: ctype=''
    v=Vocab.objects.get(name='NumReqTypes')
    ctypeVals=Value.objects.filter(vocab=v)
    try:
        ctype=ctypeVals.get(value=ctype)
    except:
        logging.debug('Invalid numerical requirement type (%s) in %s,%s'%(ctype,name,id))
        ctype=None
    
    if not name or name=='':
        logging.debug('Numerical Requirement %s [%s,%s]'%(id,description,ctype))
    
    n=NumericalRequirement(description=description,name=name,ctype=ctype)
    n.save()
    return n
        
        
def metaAuthor(elem):
    ''' Oh what a nasty piece of code this is, but I don't have time to do it properly '''
    #FIXME do this properly with lxml and xpath with namespaces
    s=ET.tostring(elem)
    if s.find('Charlotte')>-1: 
        n='Charlotte Pascoe'
        c=ResponsibleParty.objects.filter(name=n)
        if len(c)==0:
            p=ResponsibleParty(name=n,abbrev=n,uri=str(uuid.uuid1()),
                               email='Charlotte.Pascoe@stfc.ac.uk')
            p.save()
        else: p=c[0]
    elif s.find('Gerard')>1:
        n='Gerard Devine'
        c=ResponsibleParty.objects.filter(name=n)
        if len(c)==0:
            p=ResponsibleParty(name=n,abbrev=n,uri=str(uuid.uuid1()),
                            email='g.m.devine@reading.ac.uk')
            p.save()
        else: p=c[0]
    else: p=None
    logging.debug('Metadata maintainer: %s'%p)
    return p

def duration(elem,calendar):
        if elem is None:
            return None
        try:
            etxt=getText(elem,'lengthYears')
            length=float(etxt)
        except:
            logging.info('Unable to read length from %s'%etxt)
            length=None
        d=ClosedDateRange(startDate=getText(elem,'startDate'),
                              endDate=getText(elem,'endDate'),
                              length=length,
                              calendar=calendar)
        d.save()
        logging.debug('Experiment duration %s'%d)
        return d
        
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
        ''' Reads CIM format numerical experiments, create an experiment, and then link
        the numerical requirements in as well'''
        
        etree=ET.parse(filename)
        logging.debug('Parsing experiment filename %s'%filename)
	
        root=etree.getroot()
        
        #basic document stuff, note q'naire doc not identical to experiment bits ...
        doc={'description':'description','shortName':'abbrev','longName':'title'}
        for key in doc:
            self.__setattr__(doc[key],getText(root,key))
        
        self.rationale=getText(root,key)
        #calendar before date
        self.calendar=calendar(root.find('{%s}calendar'%cimv))
        self.requiredDuration=duration(root.find('{%s}requiredDuration'%cimv),self.calendar)
        
        # going to ignore the ids in the file, and be consistent with the rest of the q'naire
        # documents
      
        # bypass reading all that nasty gmd party stuff ...
        author=metaAuthor(root.find('{%s}author'%cimv))

        E=Experiment(rationale=self.rationale,
                     description=self.description,
                     uri=str(uuid.uuid1()),
                     abbrev=self.abbrev,
                     title=self.title,
                     requiredDuration=self.requiredDuration,
                     requiredCalendar=self.calendar,
                     metadataMaintainer=author)
        E.save()
        
        for r in root.findall('{%s}numericalRequirement'%cimv):
            n=numericalRequirement(r)
            E.requirements.add(n)
        
class TestFunctions(unittest.TestCase): 
    def testExperiment(self):
        import os
        d='data/experiments/'
        for f in os.listdir(d):
            if f.endswith('.xml'):
                x=NumericalExperiment(os.path.join(d, f)) 
        
        
            
        