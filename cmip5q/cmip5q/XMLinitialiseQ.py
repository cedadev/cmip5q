#
##
## This file for all the initialisation that SHOULD come from XML but currently
## doesn't.
##
##

from protoq.models import *
import uuid

#this tuple should provide the PCMDI controlled vocabulary for centre names
centres=(('NCAS','UK National Centre for Atmospheric Science'),
         ('NCAR','US National Centre for Atmospheric Research'),
         ('MOHC','UK Met Office Hadley Centre'),
         ('GFDL','US Geophysical Fluid Dynamics Laboratory'),
         ('IPSL','FR Institute Simone Pierre Laplace'),
         ('MPIM','DE Max Planck Institute for Meteorology'), 
         ('CMIP5','Dummy Centre used to hold model template'),
     )
     
# this is the controlled vocabulary for realms:
# that is, the top level areas under the model definitions.
realms = ('LandIce','Ocean','SeaIce','Atmosphere','OceanBiogeoChemistry','AtmosChemAndAerosols','Aerosol','LandSurface')
             
# controlled vocabulary for file formats
FileFormats=('NetCDF','Grib','PP','Excel','Text','HDF','Other')
             
# this tuple should provide a controlled vocabulary for referenceTypes
referenceTypes=('Webpage','Online Refereed',
                'Offline Refereed','Online Other',
                'Offline Other')

# these support couplings 
couplingTypes=('ESMF','OASIS3','OASIS4','Other')
spatialRegridding=('None','Weighted Nearest Neighbour','Weights and Addresses File',
                   'Bilinear','Bicubic','Conservative','Other')
temporalRegridding=('lastAvailable','linearBetween','averaged')
frequencies=('seconds','minutes','hours','days','months','years','decades')

# and these will support platforms
hardware=('Vector','Parallel','Beowulf')
#following extended from top500 site:
processorFamily=('NEC','Sparc','Intel IA-64','Intel EM64T','AMD X86_64','Other Intel','Other AMD','Other')
interconnectFamily=('Myrinet','Quadrics','Gigabit Ethernet','Infiniband','Mixed','NUMAlink','SP Switch',
    'Cray Interconnect','Fat Tree','Other')
    
#geneology 
relations=('higherResoutionVersionOf','lowerResolutionVersionOf','laterVersionOf')

#types of conformance, we'll allow more than one to be chosen
conformanceTypes=('BoundaryCondition','InitialCondition', 'CodeModification')

# types of numerical requirement (nb: at the moment we don't use these, it's hardwired)
# would need to modify the numerical requiremnet class, and the conformance code.
numrecTypes=('BoundaryCondition','InitialCondition')

def loadvocab(name,values):
    ''' Used to load vocabularies '''
    v=Vocab(uri=str(uuid.uuid1()),name=name)
    v.save()
    for r in values:
        rv=Value(vocab=v,value=r)
        rv.save()

def initialise():
    '''This routine initialises the CMIP5 questionaire '''
    
    #start with initialising the centres:
    for centre in centres:
        u=str(uuid.uuid1())
        c=Centre(abbrev=centre[0],title=centre[1],uri=u)
        c.save()
    
    #add the realm vocabularies
    loadvocab('Realms',realms)
        
    #now add reference type vocabulary
    loadvocab('Reference Types Vocab',referenceTypes)
    
    #now add couplings vocabularies
    loadvocab('couplingType',couplingTypes)
    loadvocab('FreqUnits',frequencies)
    loadvocab('SpatialRegridding',spatialRegridding)
    loadvocab('TemporalRegridding',temporalRegridding)
    
    #support for platforms
    loadvocab('hardwareType',hardware)
    loadvocab('processorType',processorFamily)
    loadvocab('interconnectType',interconnectFamily)
    
    #support for geneologies
    loadvocab('relations',relations)
    
    #support for conformanceTypes and numericalRequirementTypes
    loadvocab('conformanceTypes',conformanceTypes)
    loadvocab('numericalRequirementTypes',numrecTypes)
    
    #support for file formats
    loadvocab('FileFormats',FileFormats)