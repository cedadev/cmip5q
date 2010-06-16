# -*- coding: utf-8 -*-

from django.core.management import setup_environ
import settings
setup_environ(settings)

#from ControlledModel import *
from cmip5q.protoq.tests import *

if __name__=="__main__":
    unittest.main()