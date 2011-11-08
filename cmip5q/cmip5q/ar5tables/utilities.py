'''
Utilities module for general AR5 table-related functions

Created on 23 Sep 2011

@author: gerarddevine
'''

from cmip5q.protoq.models import *  


def get_lsrivrout(model):
    '''
    Returns whether river routing is implemented
    '''
    try:
        c = Component.objects.filter(
                                    scienceType='RiverRouting').get(model=model)
        
        if c.implemented:
            riverrouting = 'Yes'
        else:
            riverrouting = 'No'
    except:
        riverrouting = ''
        
    #Get my own url
    cen = Centre.objects.get(component=c)
    myurl =reverse('cmip5q.protoq.views.componentEdit',args=(cen.id, c.id))
    
    return riverrouting, myurl



def get_silatmelt(model):
    '''
    retrieve yes/no for sea ice lateral melting
    '''
    
    try:
        #get the Ice level component
        sciencetype = 'SeaIceThermodynamics'
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the 'General Attributes' parameter group
        pg = ParamGroup.objects.filter(name='Ice').get(component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        
        #and now the individual or parameter
        bp = BaseParam.objects.filter(constraint=cg[0]).get(name='Processes')
        op = OrParam.objects.get(baseparam_ptr=bp)                        
        
        silatmelt = 'No'
        for op in op.value.values():
            if op['name'] == 'Sea ice lateral melting':
                silatmelt = 'Yes'
                
    except:
        silatmelt = 'No'
    
    #Get my own url
    cen = Centre.objects.get(component=c)
    myurl =reverse('cmip5q.protoq.views.componentEdit',args=(cen.id, c.id))
    
    return silatmelt, myurl


def get_siwaterpond(model):
    '''
    retrieve yes/no for sea ice water ponds
    '''
    
    try:
        #get the Thermodynamics level component
        sciencetype = 'SeaIceThermodynamics'
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the 'General Attributes' parameter group
        pg = ParamGroup.objects.filter(name='General Attributes').get(
                                                                    component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.get(parentGroup=pg)
        
        #and now the individual xor parameter
        bp = BaseParam.objects.filter(constraint=cg).get(name='WaterPonds')
        xp = XorParam.objects.get(baseparam_ptr=bp)                        
        
        siwaterpond = xp.value
    
    except:
        siwaterpond = ''
    
    #Get my own url
    cen = Centre.objects.get(component=c)
    myurl =reverse('cmip5q.protoq.views.componentEdit',args=(cen.id, c.id))
    
    return siwaterpond, myurl


def get_sirheology(model):
    '''
    Retrieves the ocean free slip type
    '''
    
    try:
        #get the ocean OceanUpAndLowBoundaries level component
        sciencetype = 'SeaIceDynamics'
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the 'General Attributes' parameter group
        pg = ParamGroup.objects.filter(name='General Attributes').get(
                                                                    component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.get(parentGroup=pg)
        
        #and now the individual xor parameter for 'Type'
        bp = BaseParam.objects.filter(constraint=cg).get(name='Rheology')
        xp = XorParam.objects.get(baseparam_ptr=bp)                        
        
        sirheol = xp.value
    
    except:
        sirheol = ''
    
    #Get my own url
    cen = Centre.objects.get(component=c)
    myurl =reverse('cmip5q.protoq.views.componentEdit',args=(cen.id, c.id))
    
    return sirheol, myurl


def get_oceanTopBC(model):
    '''
    Retrieves the ocean free slip type
    '''
    
    try:
        #get the ocean OceanUpAndLowBoundaries level component
        sciencetype = 'OceanUpAndLowBoundaries'
        c = Component.objects.filter(scienceType=sciencetype).get(model=model)
        #get the 'free surface' parameter group
        pg = ParamGroup.objects.filter(name='FreeSurface').get(component=c)
        #Now get the constraint group
        cg = ConstraintGroup.objects.get(parentGroup=pg)
        
        #and now the individual xor parameter for 'Type'
        bp = BaseParam.objects.get(constraint=cg)
        xp = XorParam.objects.get(baseparam_ptr=bp)                        
        
        topbc = xp.value
    
    except:
        topbc = ''
    
    return topbc


def get_ZCoord(model, sciencetype):
    '''
    Gets the z co-ordinate for a supplied model
    '''
    
    try:
        #get the atmosphere level component
        c = Component.objects.filter(isRealm=True).filter(
                                    scienceType=sciencetype).get(model=model)
        
        #get the two subgrids (hor and vert)
        grids = c.grid.grids.all()            
        #identify all vertical grid paramgroups            
        vpgs = ParamGroup.objects.filter(name='VerticalCoordinateSystem')
        #narrow down the selection to specific vertical grid
        vertgrid = grids.get(paramGroup__in=vpgs)
        #and now the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=vertgrid).get(
                                                name='VerticalCoordinateSystem')
        
        #Now get the constraint group (doesn't have a title)
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        # and then Grid Resolution value
        gr = BaseParam.objects.filter(constraint__in=cg).get(
                                                name='VerticalCoordinateType')
        gridres = XorParam.objects.get(baseparam_ptr=gr).value
        
        #Now get the constraint group for the chosen VerticalCoordinateType
        vctstring= 'if VerticalCoordinateType is "%s"' %str(gridres)
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                                        constraint=vctstring)
        
        #and now the individual keyboard parameter for 'VerticalCoordinate'
        bp = BaseParam.objects.filter(constraint=cg).get(name='VerticalCoordinate')
        xp = XorParam.objects.get(baseparam_ptr=bp)                        
        
        zcoord = xp.value
                
    except:
        zcoord = ''
    
    return zcoord


def get_HorGridRes(model, sciencetype, mnemonic=False):
    '''
    Gets the horizontal grid resolution (and optionnaly the mnemonic) for a 
    component of a supplied model
    '''
    
    try:
        #get the component level component
        c = Component.objects.filter(isRealm=True).filter(
                            scienceType=sciencetype).get(model=model)
        
        #get the two subgrids (hor and vert)
        grids = c.grid.grids.all()            
        #identify all horizontal grid paramgroups            
        hpgs = ParamGroup.objects.filter(name='HorizontalCoordinateSystem')
        
        #narrow down the selection to specific horizontal grid
        horgrid = grids.get(paramGroup__in=hpgs)
        #and now the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=horgrid).get(
                                        name='HorizontalCoordinateSystem')
        
        #Now get the constraint group (doesn't have a title)
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        # and then Grid Resolution value
        gr = BaseParam.objects.filter(constraint__in=cg).get(
                                                        name='GridResolution')
        gridres = KeyBoardParam.objects.get(baseparam_ptr=gr).value
        # and optionally the mnemonic
        if mnemonic:
            gm = BaseParam.objects.filter(constraint__in=cg).get(
                                                        name='GridMnemonic')
            gridmnem = KeyBoardParam.objects.get(baseparam_ptr=gm).value
        
                           
    except:
        gridmnem = ''
        gridres = ''
    
    if mnemonic:
        return gridmnem, gridres
    else:
        return gridres


def get_atmGrid(model):
    '''
    Gets the horizontal resolution/grid name for the atmosphere component of a 
    supplied model
    '''
    
    try:
        #get the atmosphere level component
        c = Component.objects.filter(isRealm=True).filter(
                                    scienceType='Atmosphere').get(model=model)
        
        #get the two subgrids (hor and vert)
        grids = c.grid.grids.all()            
        #identify all horizontal grid paramgroups            
        hpgs = ParamGroup.objects.filter(name='HorizontalCoordinateSystem')
        
        #narrow down the selection to specific horizontal grid
        horgrid = grids.get(paramGroup__in=hpgs)
        #and now the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=horgrid).get(
                                            name='HorizontalCoordinateSystem')
        
        #Now get the constraint group (doesn't have a title)
        cg = ConstraintGroup.objects.filter(parentGroup=pg)
        # and then the GridMnemonic and Grid Resolution values
        gm = BaseParam.objects.filter(constraint__in=cg).get(
                                                        name='GridMnemonic')
        gr = BaseParam.objects.filter(constraint__in=cg).get(
                                                        name='GridResolution')
        atmosgridmnem = KeyBoardParam.objects.get(baseparam_ptr=gm).value
        atmosgridres = KeyBoardParam.objects.get(baseparam_ptr=gr).value
                           
    except:
        atmosgridmnem = ''
        atmosgridres = ''
    
    return atmosgridmnem, atmosgridres
                

def get_atmTopLevel(model):
    '''
    Gets the top level for a supplied model
    '''
    
    try:
        #get the atmosphere level component
        c = Component.objects.filter(isRealm=True).filter(
                                    scienceType='Atmosphere').get(model=model)
        
        #get the two subgrids (hor and vert)
        grids = c.grid.grids.all()            
        #identify all vertical grid paramgroups            
        vpgs = ParamGroup.objects.filter(name='VerticalExtent')
        #narrow down the selection to specific vertical grid
        vertgrid = grids.get(paramGroup__in=vpgs)
        #and now the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=vertgrid).get(name='VerticalExtent')
        #Now get the constraint group for 'atmospheric domain'
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                                        constraint='if Domain is "atmospheric"')
        #and now the individual keyboard parameter for 'TopModelLevel'
        bp = BaseParam.objects.filter(constraint=cg).get(name='TopModelLevel')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)                        
        
        atmosgridtop = kp.value
        
    except:
        atmosgridtop = ''
    
    return atmosgridtop


def get_Refs(model, sciencetype):
    '''
    Returns references associated with a particular component of a model
    '''
    try:
        c = Component.objects.filter(isRealm=True).filter(
                                    scienceType=sciencetype).get(model=model)
        refs = c.references.all()
        refslist = []
        refscits=[]
        for ref in refs:
            refslist.append(ref.name)
            refscits.append(ref.citation)
    except:
        refslist = []
        refscits = []
    
    return refslist, refscits


def getModels():
    '''
    Returns a list of actual models, i.e. not example, test centre, or dups 
    '''
    
    centres = Centre.objects.all()
    #remove CMIP5, example, and test centres
    for ab in ['CMIP5','1. Example','2. Test Centre']:
        centres = centres.exclude(abbrev=ab)
        
    models = Component.objects.filter(isModel=True).filter(
                                    isDeleted=False).filter(
                                    centre__in=centres).order_by('centre')
    #remove model duplicates (assuming these are not meant to be real instances
    for abb in ['Model Template dup', 'Model Template dupcp']:
        models = models.exclude(abbrev=abb)
    
    return models


def getExps():
    '''
    Returns the full list of current experiments 
    '''
    
    exps = Experiment.objects.all().filter(
                                    isDeleted=False)
            
    return exps




