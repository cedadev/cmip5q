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
             )
             
# this tuple should provide a controlled vocabulary for referenceTypes
referenceTypes=('Webpage','Online Refereed Publication',
                'Offline Refereed Publication','Online Document',
                'Offline Document')

# these support couplings 
couplingTypes=('None','offline','OASIS2','OASIS3','OASIS4','Other')
interpolationTypes=('None','Weighted Nearest Neighbour','Weights and Addresses File',
                   'Bilinear','Bicubic','Conservative','Other')
interpolationDims=('2D','3D')
frequencies=('seconds','minutes','hours','days','months','years','decades')

# and these will support platforms
hardware=('Vector','Cluster','Parallel')

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
        
    #now add reference type vocabulary
    loadvocab('Reference Types Vocab',referenceTypes)
    
    #now add couplings vocabularies
    loadvocab('couplingType',couplingTypes)
    loadvocab('couplingFreq',frequencies)
    loadvocab('couplingInterp',interpolationTypes)
    loadvocab('couplingDim',interpolationDims)
    
    #support for platforms
    loadvocab('HardwareType',hardware)
    