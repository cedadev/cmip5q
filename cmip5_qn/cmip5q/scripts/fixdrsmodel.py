'''
Miscellaneous script to fix mismatch between sim model and related drs model
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
f = open('fixeddrs.txt','w')
f.write('temporary file \n')
f.write(' \n')

# 1. for each drs item
for drs in DRSOutput.objects.all().order_by('id'):
    # 2. get the parent simulation
    basesims = Simulation.objects.filter(isDeleted=False).filter(drsOutput__id=drs.id)
    if len(basesims) == 1:
        #get the simulation model
        simmodel = basesims[0].numericalModel
        #get the drsoutput model
        drsmodel = drs.model
        if drs.model != simmodel:
            f.write('MODEL MISMATCH')
            f.write('institution = %s \n' % basesims[0].centre)
            f.write('Simulation = %s \n' % basesims[0])
            f.write('Sim model = %s \n' % simmodel)
            f.write('Drs model = %s \n' % drsmodel)
            f.write('\n')
    else:
        print 'Got zero or more than one drs associated, %s' % len(basesims)
        for x in Simulation.objects.filter(drsOutput__id=drs.id):
            if not x.isDeleted:
                print 'IS NOT DELETED!!!!!!'