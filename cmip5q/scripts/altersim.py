#!/usr/bin/env python

'''
Miscellaneous script for debugging purposes.
'''



#from django.core.management import setup_environ
#import settings
#setup_environ(settings)
#imports
import os
import sys

# putting project and application into sys.path  
sys.path.insert(0, os.path.expanduser('..\protoq'))
sys.path.insert(1, os.path.expanduser('..\..\cmip5q'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cmip5q.protoq.models import *

#---- Code below here ------

allcdocs=[]
for cdoc in CIMObject.objects.filter(cimtype='simulation'):
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    if basesim.ensembleMembers > 1:
        actcdoc = list(CIMObject.objects.filter(uri=basesim.uri).order_by('documentVersion'))[-1]
        if actcdoc not in allcdocs:
            allcdocs.append(actcdoc)

for cdoc in allcdocs:
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    print str(cdoc.title)+'        '+str(basesim.id)+'        '+str(basesim.centre)+'        '+str(basesim.centre.id)+'        '+str(basesim.abbrev)
