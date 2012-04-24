#!/usr/bin/env python
'''
Miscellaneous script for adding start years to modified DRSOutput instances

'''

import os
import sys
import logging

# putting project and application into sys.path
sys.path.insert(0, os.path.expanduser(
                        '/home/gerarddevine/dev/django/questionnaire/cmip5q/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmip5q.settings'

from django.core.management import setup_environ

from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import *

# 1. for each drs item
for drs in DRSOutput.objects.all().order_by('id'):
    # 2. get the parent simulation
    print drs.id
    basesims = Simulation.objects.filter(isDeleted=False).filter(drsOutput__id=drs.id)
    if len(basesims):
        #check for any missing drs rip values
        try:
            ripvalue = basesims[0].drsMember
            print ripvalue
            if not drs.member:
                print 'I am empty'
                drs.member = ripvalue
                drs.save()
        except:
            print 'Unable to assign drs value'


for drs in DRSOutput.objects.all().order_by('id'):
    # 2. get the parent simulation
    print drs.id
    basesims = Simulation.objects.filter(isDeleted=False).filter(drsOutput__id=drs.id)

    if len(basesims):
        try:
            # 3. get that simulations' start year
            startyear = basesims[0].duration.startDate.year
            if not drs.startyear:
                drs.startyear = startyear
                drs.save()
        except:
            print 'Unable to assign start year'