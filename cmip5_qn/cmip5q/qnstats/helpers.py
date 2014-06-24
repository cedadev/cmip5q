''' Helper utilities for qnstats application

Created on 13 Sep 2012

@author: gerarddevine
'''

from cmip5q.protoq.models import *

def cmip5_centres():
    '''Returns a queryset of cmip5 centres, omitting Example centre etc
    
    '''
    centres = Centre.objects.all()
    
    #remove CMIP5, example, and test centres
    for ab in ['CMIP5', '1. Example', '2. Test Centre']:
        centres = centres.exclude(abbrev=ab)
    
    
    return centres