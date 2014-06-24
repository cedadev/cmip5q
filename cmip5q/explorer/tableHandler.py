'''
Module to handle the generation of explorer tables from information supplied to 
the CMIP5 questionnaire

@author: gerard devine
'''

from cmip5q.explorer.dbvalues import *
from cmip5q.protoq.models import NumericalRequirement


def modeldesctable(models):
    ''' Generates all information necessary for AR5 table 1 (i.e. the model 
    description table)
     
    '''
    
    for m in models:
        
        # 0. get top level info
        
        #Get the main model reference(s)
        m.mainrefs, m.maincits = get_Refs(m, 'model')
        
        # 1. Get aerosol column information
        
        #Check that realm is implemented
        m.aerimplemented = is_compimpl(m, 'Aerosols')

        if not m.aerimplemented:
            m.aerabbrev = m.aerrefs = m.aercits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.aerabbrev = get_compabbrev(m, 'Aerosols')
            #Get the component references
            m.aerrefs, m.aercits = get_Refs(m, 'Aerosols')                

        # 2. Get atmosphere column information
          
        #Check that realm is implemented
        m.atmosimplemented = is_compimpl(m, 'Atmosphere')
        if m.atmosimplemented:
            #Get the abbrev
            m.atmosabbrev = get_compabbrev(m, 'Atmosphere')
            #Get the component references
            m.atmosrefs, m.atmoscits = get_Refs(m, 'Atmosphere')
            #Get vertical grid info
            m.atmosgridtop, m.atmosnumlevels = get_vertgridinfo(m, 'Atmosphere')
            #Get horizontal grid menmonic and resolution
            atmosgridres, atmosgridmnem = get_HorGridRes(m, 'Atmosphere', 
                                                         mnemonic=True)
            m.atmoshorgrid = atmosgridmnem+' '+ atmosgridres
                
        
        # 3. Get atmospheric chemistry column information
        
        #Check that realm is implemented
        m.atmchemimplemented = is_compimpl(m, 'AtmosphericChemistry')
        if not m.atmchemimplemented:
            m.atmchemabbrev = m.atmchemrefs = m.atmchemcits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.atmchemabbrev = get_compabbrev(m, 'AtmosphericChemistry')
            #Get the component references
            m.atmchemrefs, m.atmchemcits = get_Refs(m, 'AtmosphericChemistry')
        
        
        # 4. Get land ice column information
        
        #Check that realm is implemented
        m.liceimplemented = is_compimpl(m, 'LandIce')
        if not m.liceimplemented:
            m.liceabbrev = m.licerefs = m.licecits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.liceabbrev = get_compabbrev(m, 'LandIce')
            #Get the component references
            m.licerefs, m.licecits = get_Refs(m, 'LandIce')
        
        
        # 5. Get land surface column information
        
        #Check that realm is implemented
        m.lsurfimplemented = is_compimpl(m, 'LandSurface')
        if not m.lsurfimplemented:
            m.lsurfabbrev = m.lsurfrefs = m.lsurfcits = 'Not Implemented'
        else:
            #Get the abbrev
            m.lsurfabbrev = get_compabbrev(m, 'LandSurface')
            #Get the component references
            m.lsurfrefs, m.lsurfcits = get_Refs(m, 'LandSurface')
        
        
        # 6. Get Ocean Biogeo column information
        
        #Check that realm is implemented
        m.obgcimplemented = is_compimpl(m, 'OceanBiogeoChemistry')
        if not m.obgcimplemented:
            m.obgcabbrev = m.obgcrefs = m.obgccits = 'Not Implemented'
        else:
            #Get the abbrev
            m.obgcabbrev = get_compabbrev(m, 'OceanBiogeoChemistry')
            #Get the component references
            m.obgcrefs, m.obgccits = get_Refs(m, 'OceanBiogeoChemistry')
        
        
        # 7. Get Ocean information
        
        #Check that realm is implemented
        m.oceanimplemented = is_compimpl(m, 'Ocean')
        if not m.oceanimplemented:
            m.oceanabbrev = 'Not Implemented' 
            m.oceanrefs = 'Not Implemented'
            m.oceancits = 'Not Implemented'
            m.oceanhorgrid = 'Not Implemented'
            m.oceannumlevels = 'Not Implemented'
            m.oceanzcoord = 'Not Implemented'
            m.oceantoplevel = 'Not Implemented'
            m.oceantopbc = 'Not Implemented'
        else:
            #Get the abbrev
            m.oceanabbrev = get_compabbrev(m, 'Ocean')
            #Get the component references
            m.oceanrefs, m.oceancits = get_Refs(m, 'Ocean')
            #Get vert grid info
            m.oceantoplevel, m.oceannumlevels = get_vertgridinfo(m, 'Ocean')
            #Get the ocean grid z co-ordinate
            m.oceanzcoord = get_ZCoord(m, 'Ocean')
            #Get the ocean top BC
            m.oceantopbc = get_oceanTopBC(m)
            #Get horizontal grid menmonic and resolution
            oceangridres, oceangridmnem = get_HorGridRes(m, 'Ocean', 
                                                         mnemonic=True)
            m.oceanhorgrid = oceangridmnem+' '+ oceangridres
        
        
        # 8. Get Sea Ice column information
        
        #Check that realm is implemented
        m.seaiceimplemented = is_compimpl(m, 'SeaIce')
        if not m.seaiceimplemented:
            m.seaiceabbrev = m.seaicerefs = m.seaicecits = 'Not Implemented'
        else:
            #Get the abbrev
            m.seaiceabbrev = get_compabbrev(m, 'SeaIce')
            #Get the component references
            m.seaicerefs, m.seaicecits = get_Refs(m, 'SeaIce')
        
    return models


def ch09table(models):
    '''
    Generates all information necessary for AR5 ch09 table 
    '''
    
    for m in models:        
        
        # Get Model assembly information including any related constraints
        m.modelassembly, \
        m.assemblyotherinstitutes,\
        m.assemblyconsortium, \
        m.mixedassemblynames, \
        m.offshelfinst = get_modelassembly(m)
        
        #get any additional info supplied under the model development section
        m.modeldevothers = get_modeldevothers(m)
        
        
        # Get Model Tuning information
        m.meanstateglobmets = get_meanstateglobmets(m)
        m.obstrendsmets = get_obstrendsmets(m)
        m.meanstateregmets = get_meanstateregmets(m)
        m.tempvarmets = get_tempvarmets(m)
        m.adjparams = get_adjparams(m)
        m.othmodtuning = get_othmodtuning(m)
        
        #get any additional info supplied under the tuning section
        m.tuningsectothers = get_tuningsectothers(m)
           
        # Get Conservation of integral quantities information
        m.intconservation = get_intconservation(m)
        m.spectuning = get_spectuning(m)
        m.fluxcorrused = get_fluxcorrused(m)
        if m.fluxcorrused == 'Yes':
            m.fluxcorrfields = get_fluxcorrfields(m)
            m.fluxcorrmeth = get_fluxcorrmeth(m)
        else:
            m.fluxcorrfields = ['N/A']
            m.fluxcorrmeth = 'N/A'
        
        #get any additional info supplied under the conservation of integral 
        # quantities section
        m.consintegothers = get_consintegothers(m)
                
    return models


def chemtable(models):
    '''
    Generates all information necessary for AR5 chemistry table 
    '''
    
    for m in models:        
        
        # Is land surface carbon cycle implemented?
        m.lsccimplemented = is_compimpl(m, 'LandSurfaceCarbonCycle')
        # Is ocean bio chemistry (carbon cycle) implemented?
        m.occimplemented = is_compimpl(m, 'OceanBiogeoChemistry')
        
        # How are aerosols represented, mass/volume, number etc?
        m.aermoments = get_aermoments(m)
        
        # What type of aerosol model scheme
        m.aerscheme = get_aerscheme(m)
        
        # What type of aerosol model scheme
        m.ocbiotracnuts = get_ocbiotracnuts(m)
        
                        
    return models


def ar5table2(exps):
    '''
    Generates all information necessary for AR5 table 2 (i.e. the experiment 
    description table) 
    '''
    
    # Harvest all numerical requirements, omitting duplicates
    reqidlist = []
    reqlist = []
    
    for e in exps:
        for req in e.requirements.all():
            #first bind the req to the experiment for the template
            # Check for duplicate using docid
            if req.docid not in reqidlist:
                reqidlist.append(req.docid)
                reqlist.append(req)
    
    # Now assign true/false to individual experiment reqs if in global reqlist  
    for e in exps:
        reqsinexp = []
        for reqid in reqidlist:
            if reqid in e.requirements.all().values_list('docid', flat=True):
                reqsinexp.append('True')
            else:
                reqsinexp.append('')
        
        e.reqsinexp = reqsinexp
        
    return reqlist, exps
    
    
def ar5table3(exps, model):
    '''
    Generates all information necessary for AR5 table 2 (i.e. the experiment 
    description table) 
    '''
    
    # Harvest all numerical requirements, omitting duplicates
    reqidlist = []
    reqlist = []
    
    for e in exps:
        for req in e.requirements.all():
            #first bind the req to the experiment for the template
            # Check for duplicate using docid
            if req.docid not in reqidlist:
                reqidlist.append(req.docid)
                reqlist.append(req)
    
    # Now assign true/false to individual experiment reqs if in global reqlist  
    for e in exps:
        reqsinexp = []
        modconforms = []
        for reqid in reqidlist:
            if reqid in e.requirements.all().values_list('docid', flat=True):
                reqsinexp.append('True')
                #get the sim using the particular model for this experiment
                sim = Simulation.objects.filter(numericalModel=model, 
                                                experiment=e)
                sim = sim.filter(isDeleted='False')
                # check current model conforms if it has been run for this exp
                if sim:
                    #first get all reqs associated with the experiment
                    ereqs = e.requirements.all()
                    #get the actual requirement
                    reqs =  GenericNumericalRequirement.objects.filter(
                                                                    docid=reqid)
                    #pull out the common requirement (must be better 
                    #way of doing this!)
                    
                    conf = Conformance.objects.filter(simulation=sim[0]).filter(
                                                                requirement=req)
                    modconforms.append('True')
                else:
                    modconforms.append('') 
            else:
                reqsinexp.append('')
                #mark conformance line as empty (ie doesn't come into play here)
                modconforms.append('')
        
        e.reqsinexp = reqsinexp
        e.modconforms = modconforms

    return reqlist, exps

    # Now assign conformant/not conformant/not applicable for each model
    # to individual experiment reqs
    for e in exps:
        #get the simulation using the particular model for this experiment
        sim = Simulation.objects.filter(numericalModel=model, experiment=e)
        sim = sim.filter(isDeleted='False')

        #get the confomances for this simulation
        confs = Conformance.objects.filter(simulation=sim[0])

        #iterate through and tag conformance existance/type
        modelconforms = []

        for reqid in reqidlist:
            if reqid in e.requirements.all().values_list('docid', flat=True):
                reqsinexp.append('True')
            else:
                reqsinexp.append('')

        e.reqsinexp = reqsinexp

    return reqlist, exps


def strattable(models):
    '''
    Generates all information necessary for strat model table
    '''

    for m in models:
        # Get the main model reference(s)
        m.mainrefs, m.maincits = get_Refs(m, 'model')

        # Atmosphere information
        m.atmosimplemented = is_compimpl(m, 'Atmosphere')
        if m.atmosimplemented:
            # Get the abbrev
            m.atmosabbrev = get_compabbrev(m, 'Atmosphere')
            # Get the component references
            m.atmosrefs, m.atmoscits = get_Refs(m, 'Atmosphere')
            # Get vert grid info
            m.atmosgridtop, m.atmosnumlevels = get_vertgridinfo(m,
                                                                'Atmosphere')
            # Get horizontal grid menmonic and resolution
            atmosgridres, atmosgridmnem = get_HorGridRes(m, 'Atmosphere',
                                                         mnemonic=True)
            m.atmoshorgrid = atmosgridmnem + ' ' + atmosgridres
            # Get OR values
            m.oroggwsrcs, m.oroggwsrcurl = get_orvalues(m,
                                        sciencetype='AtmosOrographyAndWaves',
                                        pgname='OrographicGravityWaves',
                                        bpname='SourceMechanisms')
            m.oroggwprop, m.oroggwpropurl = get_xorvalue(m,
                                        sciencetype='AtmosOrographyAndWaves',
                                        pgname='OrographicGravityWaves',
                                        bpname='PropagationScheme')
            m.oroggwdiss, m.oroggwdissurl = get_xorvalue(m,
                                        sciencetype='AtmosOrographyAndWaves',
                                        pgname='OrographicGravityWaves',
                                        bpname='DissipationScheme')

        # Atmospheric chemistry column information
        m.atmchemimplemented = is_compimpl(m, 'AtmosphericChemistry')
        if m.atmchemimplemented:
            # Get the abbrev
            m.atmchemabbrev = get_compabbrev(m, 'AtmosphericChemistry')
            # Get the component references
            m.atmchemrefs, m.atmchemcits = get_Refs(m, 'AtmosphericChemistry')
            # Get OR values
            m.strathetchemgas, m.strathetchemgasurl = get_orvalues(m,
                                        sciencetype='StratosphericHeterChem',
                                        pgname='Species',
                                        bpname='GasPhase')
            m.strathetchemaer, m.strathetchemaerurl = get_orvalues(m,
                                        sciencetype='StratosphericHeterChem',
                                        pgname='Species',
                                        bpname='Aerosol')

        # Grid info
        if m.atmosimplemented:
            # Get vertical atmosphere grid info
            m.numlevels, \
            m.topmodellevel, \
            m.levsbelow850, \
            m.levsabove200 = get_atmosvertgridinfo(m)

    return models
