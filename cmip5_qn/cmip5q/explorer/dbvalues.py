'''
Utilities module for pulling information out of the CMIP5 qn database

@author: gerarddevine
'''

import re

from cmip5q.protoq.models import *
from cmip5q.explorer.db_helpers import *


#------------------------------------------------------------------------------
# Generic values
#------------------------------------------------------------------------------


def get_Refs(model, sciencetype):
    '''
    Returns references associated with a particular component of a model, 
    including the abbreviation and the full citation
    '''
    
    try:
        if sciencetype is not "model":
            c = Component.objects.filter(isRealm=True).filter(
                                    scienceType=sciencetype).get(model=model)
        else:
            c = Component.objects.filter(isModel=True).filter(
                                    scienceType=sciencetype).get(model=model)
        refs = c.references.all()
        refslist = []
        refscits = []
        for ref in refs:
            refslist.append(ref.name)
            refscits.append(ref.citation)
    except:
        refslist = []
        refscits = []

    return refslist, refscits


def getModels(pubonly=False):
    '''
    Returns a list of actual models, i.e. not example, test centre, or dups

    The pubonly attribute dictates whether or not models that have not been
    published are included
    '''
    centres = Centre.objects.all()
    #remove CMIP5, example, and test centres
    for ab in ['CMIP5', '1. Example', '2. Test Centre']:
        centres = centres.exclude(abbrev=ab)

    models = Component.objects.filter(isModel=True).filter(
                                    isDeleted=False).filter(
                                    centre__in=centres).order_by('centre')
    #remove model duplicates (assuming these are not meant to be real instances
    for abb in ['Model Template dup', 'Model Template dupcp']:
        models = models.exclude(abbrev=abb)

    if pubonly == True:
        # Exclude models that have not been published whether directly, or as
        # part of a simulation
        pubmodels = models.exclude(isComplete=False)

        modelsfalse = models.exclude(isComplete=True)
        pubsimmodels = []
        for model in modelsfalse:
            if Simulation.objects.filter(numericalModel=model).filter(
                                                    isDeleted=False).filter(
                                                    isComplete=True):
                    pubsimmodels.append(model)

        allpubmodels = list(pubmodels) + pubsimmodels

        return allpubmodels

    else:
        return models


def getExps():
    '''
    Returns the full list of current experiments
    '''
    exps = Experiment.objects.all().filter(
                                    isDeleted=False)

    return exps


#------------------------------------------------------------------------------
# Top level model values
#------------------------------------------------------------------------------

def get_modelassembly(model):
    '''
    Returns the model assembly detail and the values following the choice of 
    model assembly, i.e.:
    
    assemblyotherinstitutes 
    assemblyconsortium 
    mixedassemblynames 
    offshelfinst
    
    putting in a '-' value for those that do not apply 
    '''
    
    # get the model assembly value
    try:
        massembly = get_xorvalue(model, 
                                 'model', 
                                 'Model development path', 
                                 'ModelAssembly')
    except:
        massembly = 'Not found'
        
    
    # get following constraint values
    assemblyotherinstitutes = assemblyconsortium = mixedassemblynames = offshelfinst = '----'
    
    if massembly == 'Assembled from components mostly developed in other institutions':
        c = Component.objects.filter(scienceType='model').get(model=model)
        pg = ParamGroup.objects.filter(name='Model development path').get(component=c)
        
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(constraint__contains='Assembled from components mostly developed in other institutions')
        
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint=cg)
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        
        mixedassemblynames = kp.value
    
    elif massembly == 'Developed as part of a multi-institute formal consortium':
        c = Component.objects.filter(scienceType='model').get(model=model)
        pg = ParamGroup.objects.filter(name='Model development path').get(component=c)
        
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(constraint__contains='Developed as part of a multi-institute formal consortium')
        
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint=cg)
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        
        mixedassemblynames = kp.value
    
    elif massembly == 'Assembled from a mix of in house and other institutions components':
        c = Component.objects.filter(scienceType='model').get(model=model)
        pg = ParamGroup.objects.filter(name='Model development path').get(component=c)
        
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(constraint__contains='Assembled from a mix of in house and other institutions components')
        
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint=cg)
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        
        mixedassemblynames = kp.value
    
    elif massembly == 'Mostly taken off shelf from another institution':
        c = Component.objects.filter(scienceType='model').get(model=model)
        pg = ParamGroup.objects.filter(name='Model development path').get(component=c)
        
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(constraint__contains='Mostly taken off shelf from another institution')
        
        #and now the individual parameter
        bp = BaseParam.objects.filter(constraint=cg)
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        
        mixedassemblynames = kp.value
             
             
    return massembly, \
           assemblyotherinstitutes, \
           assemblyconsortium, \
           mixedassemblynames, \
           offshelfinst


def get_modeldevothers(model):
    '''
    Returns any additional values given in the model development section
    '''
        
    modeldevothers = get_additionalvalues(model, 
                                    sciencetype='model', 
                                    name='Model development path')
    
    return modeldevothers


def get_tuningsectothers(model):
    '''
    Returns any additional values given in the tuning section
    '''
    tuningsectothers = get_additionalvalues(model, 
                                    sciencetype='model', 
                                    name='Tuning Section')
    
    return tuningsectothers


def get_consintegothers(model):
    '''
    Returns any additional values given in the Conservation of integral
    quantities section
    '''
    
    consintegothers = get_additionalvalues(model, 
                                    sciencetype='model', 
                                    name='Conservation of integral quantities')
    
    return consintegothers
 
    

def get_meanstateglobmets(model):
    '''
    Returns the mean state global metrics detail
    '''
    try:
        msglobalmets = get_orvalues(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'MeanStateGlobalMetrics')
    except:
        msglobalmets = ['Not found']

    return msglobalmets


def get_obstrendsmets(model):
    '''
    Returns the metrics of observed detail
    '''
    try:
        obstrendsmets = get_orvalues(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'ObservedTrendsMetrics')
    except:
        obstrendsmets = ['Not found']

    return obstrendsmets


def get_meanstateregmets(model):
    '''
    Returns the mean state regional metrics
    '''
    try:
        meanstateregmets = get_orvalues(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'MeanStateRegionalMetrics')
    except:
        meanstateregmets = ['Not found']

    return meanstateregmets


def get_tempvarmets(model):
    '''
    Returns the metrics of temporal variability used in model tuning? 
    '''
    try:
        tempvarmets = get_orvalues(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'TemporalVariabilityMetrics')
    except:
        tempvarmets = ['Not found']

    return tempvarmets


def get_adjparams(model):
    '''
    Returns the model parameters subject to adjustment in model tuning
    '''
    try:
        adjparams = get_orvalues(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'AdjustedParameters')
    except:
        adjparams = ['Not found']

    return adjparams


def get_othmodtuning(model):
    '''
    Returns anything else documented about model tuning
    '''
    try:
        othmodtuning = get_kpvalue(model, 
                                 'model', 
                                 'Tuning Section', 
                                 'OtherModelTuning?')
    except:
        othmodtuning = ['Not found']

    return othmodtuning


def get_intconservation(model):
    '''
    Returns details of efforts made to conserve any integral quantities 
    '''
    try:
        intconservation = get_orvalues(model, 
                                 'model', 
                                 'Conservation of integral quantities', 
                                 'IntegralConservation')
    except:
        intconservation = ['Not found']

    return intconservation


def get_spectuning(model):
    '''
    Returns specific tuning/treatment done to ensure conservation 
    '''
    try:
        spectuning = get_kpvalue(model, 
                                 'model', 
                                 'Conservation of integral quantities', 
                                 'SpecificTuning')
    except:
        spectuning = 'Not found'

    return spectuning


def get_fluxcorrused(model):
    '''
    Returns whether flux correction was used
    '''
    try:
        fluxcorrused = get_xorvalue(model, 
                                 'model', 
                                 'Conservation of integral quantities', 
                                 'FluxCorrectionUsed')
    except:
        fluxcorrused = 'Not found'

    return fluxcorrused


def get_fluxcorrfields(model):
    '''
    Returns which fields were used in the flux correction
    '''
    try:
        fluxcorrfields = get_orvalues(model, 
                                 'model', 
                                 'Conservation of integral quantities', 
                                 'FluxCorrectionFields')
    except:
        fluxcorrfields = ['Not found']

    return fluxcorrfields


def get_fluxcorrmeth(model):
    '''
    Returns the method of the flux correction
    '''
    try:
        fluxcorrmeth = get_kpvalue(model, 
                                 'model', 
                                 'Conservation of integral quantities', 
                                 'FluxCorrectionMethod')
    except:
        fluxcorrmeth = 'Not found'

    return fluxcorrmeth


#------------------------------------------------------------------------------
# Aerosol values
#------------------------------------------------------------------------------

def get_aermoments(model):
    '''
    Returns whether aerosol is mass/volume, number represented etc
    '''
    
    if is_compimpl(model, 'Aerosols'):
        aermoments = get_orvalues(model, 
                              'AerosolKeyProperties', 
                              'General Attributes', 
                              'ListOfPrognosticVariables')
        
        aermoments = "; ".join(aermoments)
         
    else:
        aermoments = 'Aerosol component not implemented'

    return aermoments


def get_aerscheme(model):
    '''
    Returns aerosol scheme type
    '''
    
    if is_compimpl(model, 'Aerosols'):
        aerscheme = get_orvalues(model, 
                              'AerosolModel', 
                              'AerosolScheme', 
                              'SchemeType')
        
        aerscheme = "; ".join(aerscheme)
         
    else:
        aerscheme = 'Aerosol component not implemented'
    
    return aerscheme


#------------------------------------------------------------------------------
# Ocean BioGeoChem values
#------------------------------------------------------------------------------

def get_ocbiotracnuts(model):
    '''
    Returns list of oceanic bio tracers list of species acting as nutrients
    '''
    
    if is_compimpl(model, 'OceanBiogeoChemistry'):
        ocbiotracnuts = get_orvalues(model, 
                              'OceanBioTracers', 
                              'Nutrients', 
                              'ListOfSpecies')
        
        ocbiotracnuts = "; ".join(ocbiotracnuts)
         
    else:
        ocbiotracnuts = 'Ocean BioGeoChem component not implemented'

    return ocbiotracnuts


#------------------------------------------------------------------------------
# Land Surface values
#------------------------------------------------------------------------------

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
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return str(riverrouting), myurl


#------------------------------------------------------------------------------
# Sea Ice values
#------------------------------------------------------------------------------

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
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return str(silatmelt), myurl


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
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return str(siwaterpond), myurl


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
    myurl = reverse('cmip5q.protoq.views.componentEdit', args=(cen.id, c.id))

    return str(sirheol), myurl


#------------------------------------------------------------------------------
# Ocean values
#------------------------------------------------------------------------------

def get_oceanTopBC(model):
    '''
    Retrieves the ocean top BC
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

    return str(topbc)


#------------------------------------------------------------------------------
# Grid values
#------------------------------------------------------------------------------

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
        vctstring = 'if VerticalCoordinateType is "%s"' % str(gridres)
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                                        constraint=vctstring)

        #and now the individual keyboard parameter for 'VerticalCoordinate'
        bp = BaseParam.objects.filter(constraint=cg).get(
                                                    name='VerticalCoordinate')
        xp = XorParam.objects.get(baseparam_ptr=bp)

        zcoord = xp.value

    except:
        zcoord = ''

    return str(zcoord)


def get_HorGridRes(model, sciencetype, mnemonic=False):
    '''
    Gets the horizontal grid resolution (and optionally the mnemonic) for a
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
        return str(gridmnem), str(gridres)
    else:
        return str(gridres)


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

    return str(atmosgridmnem), str(atmosgridres)


def get_vertgridinfo(model, sciencetype):
    '''
    Gets the vertical grid info for a supplied component
    '''
    try:
        #get the atmosphere level component
        c = Component.objects.filter(isRealm=True).filter(
                                    scienceType=sciencetype).get(model=model)

        #get the two subgrids (hor and vert)
        grids = c.grid.grids.all()
        #identify all vertical grid paramgroups
        vpgs = ParamGroup.objects.filter(name='VerticalExtent')
        #narrow down the selection to specific vertical grid
        vertgrid = grids.get(paramGroup__in=vpgs)
        #and now the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=vertgrid).get(
                                                        name='VerticalExtent')
        #Now get the constraint group
        if sciencetype == 'Atmosphere':
            cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                                 constraint='if Domain is "atmospheric"')
            # now the individual keyboard parameter for 'TopModelLevel' (atmos)
            bp = BaseParam.objects.filter(constraint=cg).get(
                                                        name='TopModelLevel')
            kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
            gridtop = kp.value
        else:
            cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                                        constraint='if Domain is "oceanic"')
            # now the individual keyboard parameter for 'UpperLevel'(for ocean)
            bp = BaseParam.objects.filter(constraint=cg).get(name='UpperLevel')
            kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
            gridtop = kp.value

        # now the individual keyboard parameter for 'NumberOfLevels'
        bp = BaseParam.objects.filter(constraint=cg).get(name='NumberOfLevels')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        numlevels = kp.value

    except:
        gridtop = ''
        numlevels = ''

    return str(gridtop), str(numlevels)


def get_atmosvertgridinfo(model):
    '''
    Gets the atmosphere vertical grid info for a supplied atmosphere component

    This function returns (1) Number of levels
                          (2) Top Model Level
                          (3) Number of levels below 850hPa
                          (4) Number of levels below 200hPa
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
        # get the actual VerticalExtent ParamGroup
        pg = ParamGroup.objects.filter(grid=vertgrid).get(
                                                        name='VerticalExtent')
        # get the constraint group
        cg = ConstraintGroup.objects.filter(parentGroup=pg).get(
                             constraint='if Domain is "atmospheric"')

        # get the individual keyboard parameter for 'NumberOfLevels'
        bp = BaseParam.objects.filter(constraint=cg).get(name='NumberOfLevels')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        numlevels = str(kp.value)

        # get the individual keyboard parameter for 'TopModelLevel'
        bp = BaseParam.objects.filter(constraint=cg).get(
                                                    name='TopModelLevel')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        topmodellevel = str(kp.value)

        # get the individual keyboard parameter for 'NumberOfLevelsBelow850hPa'
        bp = BaseParam.objects.filter(constraint=cg).get(
                                            name='NumberOfLevelsBelow850hPa')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        levsbelow850 = str(kp.value)

        # get the individual keyboard parameter for 'NumberOfLevelsAbove200hPa'
        bp = BaseParam.objects.filter(constraint=cg).get(
                                            name='NumberOfLevelsAbove200hPa')
        kp = KeyBoardParam.objects.get(baseparam_ptr=bp)
        levsabove200 = str(kp.value)

    except:
        numlevels = ''
        topmodellevel = ''
        levsbelow850 = ''
        levsabove200 = ''

    return numlevels, topmodellevel, levsbelow850, levsabove200
