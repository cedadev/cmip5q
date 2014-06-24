'''
Helpers module for pulling information out of the CMIP5 qn database

@author: gerarddevine
'''

import re

from cmip5q.protoq.models import *


def is_compimpl(model, sciencetype):
    '''
    Returns whether a component is implemented
    '''
    
    c = Component.objects.filter(scienceType=sciencetype).get(model=model)

    return c.implemented


def get_compabbrev(model, sciencetype):
    '''
    Returns a component abbrev
    '''
    try:
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        realmabbrev = c.abbrev
        
    except:
        realmabbrev = "Abbreviation could not be found"

    return str(realmabbrev)


def get_orvalues(model, sciencetype, pgname, bpname):
    '''
    Retrieves values from a questionnaire 'Or' selection
    '''

    try:
        #get the parent component
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the parameter group
        pg = ParamGroup.objects.filter(name=pgname).get(component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint__in=cg).get(name=bpname)
        op = OrParam.objects.get(baseparam_ptr=bp)

        opvals = []
        for opval in op.value.all():
            opvals.append(opval.name)

    except:
        opvals = []

    ##Get my own url
    #cen = Centre.objects.get(component=c)
    #c = Component.objects.filter(scienceType=sciencetype).get(model=model)
    #myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return opvals  # , myurl


def get_xorvalue(model, sciencetype, pgname, bpname):
    '''
    Retrieves value from a questionnaire 'XOR' selection
    '''

    try:
        #get the parent component
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the parameter group
        pg = ParamGroup.objects.filter(name=pgname).get(component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint__in=cg).get(name=bpname)
        xp = XorParam.objects.get(baseparam_ptr=bp)

        if xp.value is not None:
            xpval = str(xp.value)
        else:
            xpval = ''

    except:
        xpval = ''

    #Get my own url
    cen = Centre.objects.get(component=c)
    c = Component.objects.filter(scienceType=sciencetype).get(model=model)
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return xpval  # , myurl


def get_kpvalue(model, sciencetype, pgname, bpname):
    '''
    Retrieves value from a questionnaire 'keyboard' entry
    '''

    try:
        #get the parent component
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        
        #get the parameter group
        pg = ParamGroup.objects.filter(name=pgname).get(component=c)
        
        #Now get the constraint group
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint__in=cg).get(name=bpname)
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)

        if kp.value is not None:
            kpval = str(kp.value)
        else:
            kpval = ''

    except:
        kpval = ''

    #Get my own url
    cen = Centre.objects.get(component=c)
    c = Component.objects.filter(scienceType=sciencetype).get(model=model)
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return kpval   #,, myurl


def get_additionalvalues(model, sciencetype, name):
    '''
    Retrieves any 'other' additional values added for model dev
    '''
    
    c = Component.objects.filter(scienceType=sciencetype).get(model=model)
    pg = ParamGroup.objects.filter(name=name).get(component=c)
    cg = ConstraintGroup.objects.filter(parentGroup=pg)

    #and now the individual parameters
    othervalues = []
    bps = BaseParam.objects.filter(constraint__in=cg).filter(controlled=False)
    for bp in bps:
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        kpstring = '%s : %s' % (bp.name, kp.value)
        othervalues.append(kpstring)
    
    return othervalues
