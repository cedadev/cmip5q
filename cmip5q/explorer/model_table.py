'''
Module to handle model-based explorer tables

@author: gerard devine
'''

import datetime

from cmip5q.explorer.dbvalues import *
from cmip5q.protoq.models import NumericalRequirement


class ModelTable(object):
    '''Represents a metadata explorer table of cmip5 model properties
    
    '''
    def init(self, table_title='New model explorer table', models=None, fields=None):
        self.created = datetime.datetime.now()
        self.title = table_title
        self.models = models
        self.fields = fields
        
        for m in self.models:
            
            #---------------------------------------------
            #0. get top level info
            #---------------------------------------------
            
            #Get the main model reference(s)
            m.mainrefs, m.maincits = get_Refs(m, 'model')
            
            #---------------------------------------------
            # 1. Get aerosol column information
            #---------------------------------------------
            
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
