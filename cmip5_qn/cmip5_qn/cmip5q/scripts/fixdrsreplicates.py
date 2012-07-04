'''
Miscellaneous script to fix replicated drsoutputs to more than one simulation. 
'''

import os
import sys

# putting project and application into sys.path
sys.path.append('../cmip5q')
sys.path.append('../cmip5q/protoq')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmip5q.settings'

from django.core.management import setup_environ

from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import *

# open a file for writing
f = open('repsims.txt','w')
f.write('temporary file \n')
f.write(' \n')


# 1. for each drs item
for drs in DRSOutput.objects.all().order_by('id'):
    # 2. get the parent simulation
    basesims = Simulation.objects.filter(isDeleted=False).filter(drsOutput__id=drs.id)
    if len(basesims) > 1:
        # need to write out new drsoutputs
        print len(basesims)
        basesims = list(basesims)
        for bs in basesims[1:]:    
            f.write('Replicated sim drs= %s \n' % bs)
            f.write('Replicated sim drs id= %s \n' % bs.id)
            f.write('Replicated sim drs centre = %s \n' % bs.centre)
            f.write('\n')        
            bs.drsOutput.clear()
            # make a new DRSOutput and attach it
            d = DRSOutput(institute=bs.centre,
                          model=bs.numericalModel,
                          member=bs.drsMember,
                          experiment=bs.experiment,
                          startyear=bs.duration.startDate.year)
            d.save()
            bs.drsOutput.add(d)
    else:
        print 'No duplicates'
        
f.close()