'''
Created on 25 Jan 2012

@author: gerarddevine
'''

from cmip5q.protoq.models import *

E=Experiment()
filename = '7.4.historicalExt.xml'

etree=ET.parse(filename)
txt=open(filename,'r').read()
logging.debug('Parsing experiment filename %s'%filename)
root=etree.getroot()
getter=etTxt(root)
#basic document stuff, note q'naire doc not identical to experiment bits ...
doc={'description':'description','shortName':'abbrev','longName':'title','rationale':'rationale'}
logging.debug('AAAAAA')
for key in doc:
    E.__setattr__(doc[key],getter.get(root,key))

# load the calendar type
calendarName=root.find("{%s}calendar"%cimv)[0].tag.split('}')[1]
logging.debug('BBBBBBB')
vocab=Vocab.objects.get(name="CalendarTypes")
logging.debug('CCCCCC')
term=Term(vocab=vocab,name=calendarName)
logging.debug('CCCCCC')
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
keys=['uri','metadataVersion','documentVersion','created','updated','author','description']
attrs={}
for key in keys: attrs[key]=E.__getattribute__(key)

cfile=CIMObject(**attrs)
cfile.cimtype=E._meta.module_name
cfile.xmlfile.save('%s_%s_v%s.xml'%(cfile.cimtype,E.uri,E.documentVersion),
                       ContentFile(txt),save=False)
cfile.title='%s (%s)'%(E.abbrev,E.title)
cfile.save()