'''
External script to add a new centre to the questionnaire database

TO USE - edit the lines for centrename and centreabbrev and run.

Author: Gerard Devine
'''

import os
import sys
import uuid


# putting project and application into sys.path
sys.path.append('../cmip5q')
sys.path.append('../cmip5q/protoq')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmip5q.settings'
from django.core.management import setup_environ
from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import *

# Edit the two lines below to add new centre details
centrename = 'Instituto Nacional de Pesquisas Espaciais '
centreabbrev = 'INPE'


proceed = raw_input('Add a new centre called %s? (Y/N)' % centreabbrev)

if proceed == 'Y' or proceed =='y':
    try:
        u = str(uuid.uuid1())
        c = Centre(abbrev=centreabbrev,
                   name=centrename,
                   uri=u)
        c.isOrganisation = True
        c.save()
        #and give each of them an unknown user to play with
        rp = ResponsibleParty(name='Unknown', 
                              abbrev='Unknown', 
                              address='Erehwon', 
                              email='u@foo.bar',
                              uri=str(uuid.uuid1()),
                              centre=c)
        rp.save()
        
        print 'New centre %s added' % centreabbrev
        
    except:
        print 'Problem occurred - Centre not saved'    
    
else:
    print 'exiting script without running'
    