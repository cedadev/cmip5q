#! /usr/bin/env python
#coding:utf-8

import os
import sys

# putting project and application into sys.path
sys.path.append('/home/gerarddevine/dev/django/qn/cmip5q')
sys.path.append('/home/gerarddevine/dev/django/qn/cmip5q/protoq')
#sys.path.insert(1, os.path.expanduser('\home\gerarddevine\dev\django\qn\cmip5q'))
#sys.path.insert(0, os.path.expanduser('/home/gerarddevine/dev/django/qn/cmip5q/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmip5q.settings'

from django.core.management import setup_environ

from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import *


sims = Simulation.objects.filter(isDeleted=False)

for sim in sims:
    if not len(sim.datasets.all()):
        print sim.id
        itypes = Term.objects.filter(vocab=Vocab.objects.get(name='InputTypes')).order_by('id')
        for itype in itypes:
            d = Dataset(usage=itype)
            d.save()
            sim.datasets.add(d)

