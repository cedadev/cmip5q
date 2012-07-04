#! /usr/bin/env python
#coding:utf-8

"""
    External script to add new experiments to a live questionnaire:
    
    TO USE: from cmip5q directory issue:
       > ./py scripts/addExp.py <filename> (./py is the local badc 
       directory python)
"""

#imports
import os
import sys

# putting project and application into sys.path  
sys.path.insert(0, os.path.expanduser('..\protoq'))
sys.path.insert(1, os.path.expanduser('..\..\cmip5q'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cmip5q.protoq.models import *

  
def addExp():
    '''
    Experiments are defined in XML files, so need to be loaded into django, 
    and a copy loaded into the document database as well 
    '''
    
    filename= '6.8.Cloudresponse_UniSST.xml'
    E=Experiment()
   
    etree=ET.parse(filename)
    txt=open(filename,'r').read()
    logging.debug('Parsing experiment filename %s'%filename)
    root=etree.getroot()
    getter=etTxt(root)
    #basic document stuff, note q'naire doc not identical to experiment bits ...
    doc={'description':'description', 
         'shortName':'abbrev', 
         'longName':'title', 
         'rationale':'rationale'}
    
    for key in doc:
        E.__setattr__(doc[key],getter.get(root,key))

    # load the calendar type
    calendarName=root.find("{%s}calendar"%cimv)[0].tag.split('}')[1]
    
    vocab=Vocab.objects.get(name="CalendarTypes")
    
    term=Term(vocab=vocab,name=calendarName)
    
    term.save()
    E.requiredCalendar=term
   
    # bypass reading all that nasty gmd party stuff ...
    E.metadataMaintainer=ResponsibleParty.fromXML(root.find('{%s}author'%cimv))
    
    # do some quick length checking
    if len(E.abbrev)>25:
        old=E.abbrev
        E.abbrev=old[0:24]
        logging.info('TOOLONG: Truncating abbreviation %s to %s'%(old,E.abbrev))

    E.uri=atomuri()
    E.save()
    
    for r in root.findall('{%s}numericalRequirement'%cimv):
        #pass the constructor me and the element tree element
        n=instantiateNumericalRequirement(E,r)
        if n is not None: # n should only be None for a RequirementSet
            n.save()
            E.requirements.add(n)
  
    # we can save this most expeditiously, directly, here.
    keys=['uri', 
          'metadataVersion', 
          'documentVersion', 
          'created', 
          'updated', 
          'author', 
          'description']
    
    attrs={}
    for key in keys: attrs[key]=E.__getattribute__(key)
    
    cfile=CIMObject(**attrs)
    cfile.cimtype=E._meta.module_name
    cfile.xmlfile.save('%s_%s_v%s.xml'%(cfile.cimtype,E.uri,E.documentVersion),
                           ContentFile(txt),save=False)
    cfile.title='%s (%s)'%(E.abbrev,E.title)
    cfile.save()

           
if __name__ == '__main__':
    addExp()

