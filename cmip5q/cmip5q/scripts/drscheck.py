#! /usr/bin/env python
#coding:utf-8

"""
External script to check that a simulation has a related drsOutput associated with 
it and if not creates one (ongoing bugfix that should no longer occur)
"""

#imports
import os
import sys

# putting project and application into sys.path  
sys.path.insert(0, os.path.expanduser('..\protoq'))
sys.path.insert(1, os.path.expanduser('..\..\cmip5q'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cmip5q.protoq.models import *


sims = Simulation.objects.filter(isDeleted=False)

for sim in sims:
    if not len(sim.drsOutput.all()):
        d = DRSOutput(institute=sim.centre, 
                      model=sim.numericalModel, 
                      member=sim.drsMember, 
                      experiment=sim.experiment)
        d.save()
        sim.drsOutput.add(d)
 
