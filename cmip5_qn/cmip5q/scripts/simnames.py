#!/usr/bin/env python

'''
Miscellaneous script for outputting names (and some details) of published 
simulations (as well as searching for any non-trimmed names) 
'''

# --- Imports/setting up environment -----
from django.core.management import setup_environ
from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import Simulation, CIMObject


#---- Code below here ------

allcdocs=[]
for cdoc in CIMObject.objects.filter(cimtype='simulation'):
    # get matching simulation object
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    #retrieve the latest version...
    actcdoc = list(CIMObject.objects.filter(uri=basesim.uri).
                    order_by('documentVersion'))[-1]
    #...and add to list if not already there
    if actcdoc not in allcdocs:
        allcdocs.append(actcdoc)
            
# set up file to write to
f = open('files/simnames.text', 'w')

#write some overall details
f.write('total number of simulations exported = ' +str(len(allcdocs)) +'\n')
f.write('\n')
f.write('\n')

#write table header and data for sim names only
f.write('Sim name \n')
f.write('---------------------------------------------------------------------------------- \n')
for cdoc in allcdocs:
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    #write out individual details
    f.write(str(basesim.abbrev)+'\n')

f.write('\n')
f.write('\n')
    

#write table header and data for sim details
f.write('Sim Centre    Sim name     Sim name length      First letter     Last letter   \n')
f.write('---------------------------------------------------------------------------------- \n')
for cdoc in allcdocs:
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    #write out individual details
    f.write(str(basesim.centre)+'      '+str(basesim.abbrev)+'      '+str(len(basesim.abbrev))+'      '+str(basesim.abbrev[0])+'      '+str(basesim.abbrev[-1]) +'\n')
    f.write('\n')
    f.write('\n')

#write table header and data for sim details (with spaces)
f.write('Sim Centre    Sim name     Sim name length      First letter     Last letter   \n')
f.write('---------------------------------------------------------------------------------- \n')
for cdoc in allcdocs:
    basesim = Simulation.objects.filter(isDeleted=False).get(uri=cdoc.uri)
    #write out individual details
    if str(basesim.abbrev)[0]==' ' or str(basesim.abbrev)[-1]==' ':
        f.write(str(basesim.centre)+'      '+str(basesim.abbrev)+'      '+str(len(basesim.abbrev))+'      '+str(basesim.abbrev[0])+'      '+str(basesim.abbrev[-1]) +'\n')

    
#close file
f.close()
