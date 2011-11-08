'''
Module to handle the generation of AR5 tables from information supplied to 
the CMIP5 questionnaire

Created on 23 Sep 2011

@author: gerard devine
'''

from cmip5q.ar5tables.utilities import *


def ar5table1(models):
    '''
    Generates all information necessary for AR5 table 1 (i.e. the model table) 
    '''
    
    for m in models:
        # 1. Get atmosphere column information
        
        #Get the atmosphere component references
        m.atmosrefs, m.atmoscits = get_Refs(m, 'Atmosphere')
        
        #Get atmosphere top level
        m.atmosgridtop = get_atmTopLevel(m)
        
        #Get atmos horizontal grid menmonic and resolution
        atmosgridres, atmosgridmnem = get_HorGridRes(m, 'Atmosphere', 
                                                     mnemonic=True)
        m.atmoshorgrid = atmosgridmnem+' '+ atmosgridres
        
        # 2. Get ocean column information
        
        #Get the ocean component references
        m.oceanrefs, m.oceancits = get_Refs(m, 'Ocean')
        
        #Get ocean horizontal resolution and vertical mnemonic
        oceangridres = get_HorGridRes(m, 'Ocean', mnemonic=False)
        m.oceangrid = oceangridres  
        
        #Get the ocean grid z co-ordinate
        m.zcoord = get_ZCoord(m, 'Ocean')
        
        #Get the ocean top BC
        m.topbc = get_oceanTopBC(m)
        
        
        # 3. Get sea ice column information
                         
        #Get the seaice component references
        m.seaicerefs, m.seaicecits = get_Refs(m, 'SeaIce')
        #Get the rheology type
        m.sirheol, m.sirheolurl = get_sirheology(m)
        #Get information on water ponds (for leads)
        m.siwaterpond, m.siwpurl = get_siwaterpond(m)
        #Get information on lateral melting (for leads)
        m.silatmelt, m.silmurl = get_silatmelt(m)
        
        
        # 4. Get coupling column information
        
         
        # 5. Get land column information
        
        #Get the land surface references
        m.lsrefs, m.lscits = get_Refs(m, 'LandSurface')
        #Get information on river routing
        m.riverrouting, m.rrurl = get_lsrivrout(m)
        
        
        
        
    return models


def ar5table2(exps):
    '''
    Generates all information necessary for AR5 table 2 (i.e. the experiment table) 
    '''
    
    for e in exps:
        e.message = "hello"
        
    return exps
    
    