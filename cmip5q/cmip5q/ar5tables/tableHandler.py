'''
Module to handle the generation of AR5 tables from information supplied to 
the CMIP5 questionnaire

Created on 23 Sep 2011

@author: gerard devine
'''

from cmip5q.ar5tables.dbvalues import *
from cmip5q.protoq.models import NumericalRequirement


def ar5table1(models):
    '''
    Generates all information necessary for AR5 table 1 (i.e. the model table) 
    '''
    
    for m in models:
        
        # 0. get top level info
        
        #Get the main model reference(s)
        m.mainrefs, m.maincits = get_Refs(m, 'model')
        
        
        # 1. Get aerosol column information
        
        #Check that realm is implemented
        m.aerimplemented = get_realmimpl(m, 'Aerosols')
        
        if not m.aerimplemented:
            m.aerabbrev = m.aerrefs = m.aercits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.aerabbrev = get_realmabbrev(m, 'Aerosols')
            #Get the component references
            m.aerrefs, m.aercits = get_Refs(m, 'Aerosols')                
        
        
        # 2. Get atmosphere column information
        
        #Check that realm is implemented
        m.atmosimplemented = get_realmimpl(m, 'Atmosphere')
        if not m.atmosimplemented:
            m.atmosabbrev = \
            m.atmosrefs = \
            m.atmoscits = \
            m.atmosgridtop = \
            m.atmosnumlevels = \
            m.atmoshorgrid =  'Not Implemented'
        else:
            #Get the abbrev
            m.atmosabbrev = get_realmabbrev(m, 'Atmosphere')
            #Get the component references
            m.atmosrefs, m.atmoscits = get_Refs(m, 'Atmosphere')
            #Get vert grid info
            m.atmosgridtop, m.atmosnumlevels = get_vertgridinfo(m, 'Atmosphere')
            #Get horizontal grid menmonic and resolution
            atmosgridres, atmosgridmnem = get_HorGridRes(m, 'Atmosphere', 
                                                         mnemonic=True)
            m.atmoshorgrid = atmosgridmnem+' '+ atmosgridres
                
        
        # 3. Get atmospheric chemistry column information
        
        #Check that realm is implemented
        m.atmchemimplemented = get_realmimpl(m, 'AtmosphericChemistry')
        if not m.atmchemimplemented:
            m.atmchemabbrev = m.atmchemrefs = m.atmchemcits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.atmchemabbrev = get_realmabbrev(m, 'AtmosphericChemistry')
            #Get the component references
            m.atmchemrefs, m.atmchemcits = get_Refs(m, 'AtmosphericChemistry')
        
        
        # 4. Get land ice column information
        
        #Check that realm is implemented
        m.liceimplemented = get_realmimpl(m, 'LandIce')
        if not m.liceimplemented:
            m.liceabbrev = m.licerefs = m.licecits = 'Not Implemented' 
        else:
            #Get the abbrev
            m.liceabbrev = get_realmabbrev(m, 'LandIce')
            #Get the component references
            m.licerefs, m.licecits = get_Refs(m, 'LandIce')
        
        
        # 5. Get land surface column information
        
        #Check that realm is implemented
        m.lsurfimplemented = get_realmimpl(m, 'LandSurface')
        if not m.lsurfimplemented:
            m.lsurfabbrev = m.lsurfrefs = m.lsurfcits = 'Not Implemented'
        else:
            #Get the abbrev
            m.lsurfabbrev = get_realmabbrev(m, 'LandSurface')
            #Get the component references
            m.lsurfrefs, m.lsurfcits = get_Refs(m, 'LandSurface')
        
        
        # 6. Get Ocean Biogeo column information
        
        #Check that realm is implemented
        m.obgcimplemented = get_realmimpl(m, 'OceanBiogeoChemistry')
        if not m.obgcimplemented:
            m.obgcabbrev = m.obgcrefs = m.obgccits = 'Not Implemented'
        else:
            #Get the abbrev
            m.obgcabbrev = get_realmabbrev(m, 'OceanBiogeoChemistry')
            #Get the component references
            m.obgcrefs, m.obgccits = get_Refs(m, 'OceanBiogeoChemistry')
        
        
        # 7. Get Ocean information
        
        #Check that realm is implemented
        m.oceanimplemented = get_realmimpl(m, 'Ocean')
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
            m.oceanabbrev = get_realmabbrev(m, 'Ocean')
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
        m.seaiceimplemented = get_realmimpl(m, 'SeaIce')
        if not m.seaiceimplemented:
            m.seaiceabbrev = m.seaicerefs = m.seaicecits = 'Not Implemented'
        else:
            #Get the abbrev
            m.seaiceabbrev = get_realmabbrev(m, 'SeaIce')
            #Get the component references
            m.seaicerefs, m.seaicecits = get_Refs(m, 'SeaIce')
        
        '''
        
        # 3. Get sea ice column information

        #Check that realm is implemented
        m.oceanimplemented = get_realmimpl(m, '')
        #Get the abbrev
        m.oceanabbrev = get_realmabbrev(m, 'Ocean')
        #Get the ocean component references
        m.oceanrefs, m.oceancits = get_Refs(m, 'Ocean')                         
        #Get the seaice component references
        m.seaicerefs, m.seaicecits = get_Refs(m, 'SeaIce')
        #Get the rheology type
        m.sirheol, m.sirheolurl = get_sirheology(m)
        #Get information on water ponds (for leads)
        m.siwaterpond, m.siwpurl = get_siwaterpond(m)
        #Get information on lateral melting (for leads)
        m.silatmelt, m.silmurl = get_silatmelt(m)
        
         
        # 5. Get land column information
        
        #Get the land surface references
        m.lsrefs, m.lscits = get_Refs(m, 'LandSurface')
        #Get information on river routing
        m.riverrouting, m.rrurl = get_lsrivrout(m)
                '''
        
        
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
                #get the simulation using the particular model for this experiment
                sim = Simulation.objects.filter(numericalModel=model, experiment=e)
                sim = sim.filter(isDeleted='False')
                # check if current model conforms if it has been run for this exp
                if sim:
                    #first get all reqs associated with the experiment
                    ereqs = e.requirements.all()
                    #get the actual requirement
                    reqs =  GenericNumericalRequirement.objects.filter(docid=reqid)
                    #pull out the common requirement (must be better way of doing this!)
                    
                    conf = Conformance.objects.filter(simulation=sim[0]).filter(requirement=req)
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