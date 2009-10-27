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
         ('Example','Dummy Centre used to hold examples'),
     )
     
# this is the controlled vocabulary for realms:
# that is, the top level areas under the model definitions.

VocabList={'Realms':
     ('LandIce','Ocean','SeaIce','Atmosphere','OceanBiogeoChemistry',
     'AtmosChemAndAerosols','Aerosol','LandSurface'),
     
     # controlled vocabulary for file formats
     'FileFormats':('NetCDF','Grib','PP','Excel','Text','HDF','Other'),
             
    # this tuple should provide a controlled vocabulary for referenceTypes
    'ReferenceTypes':('Webpage','Online Refereed','Offline Refereed',
                      'Online Other','Offline Other'),

    # these support couplings 
    'couplingType':('OASIS3','OASIS4','FMS','ESMF','CCSM Flux coupler','MCT',
                    'Shared Memory','Files','Other'),
    'SpatialRegridding':('None','Non-Convervative','Conservative'),
    'SpatialRegriddingType':('2D-FirstOrder','2D-SecondOrder','2D-ThirdOrder',
                         '3D-FirstOrder','3D-SecondOrder','3d-ThirdOrder','Other'),
    'TemporalRegridding':('None','TimeAverage','TimeAccumulation','lastAvailable','Linear','Other'),
    'FreqUnits':('seconds','minutes','hours','days','months','years','decades'),

    # and these will support platforms
    'hardwareType':('Vector','Parallel','Beowulf'),

    #following extended from top500 site:
    'processorType':('NEC','Sparc','Intel IA-64','Intel EM64T','AMD X86_64',
                          'Other Intel','Other AMD','Other'),   
    'interconnectType':('Myrinet','Quadrics','Gigabit Ethernet','Infiniband','Mixed',
                        'NUMAlink','SP Switch','Cray Interconnect','Fat Tree','Other'),
    
    #geneology 
    'relations':('higherResoutionVersionOf','lowerResolutionVersionOf','laterVersionOf'),

    #types of conformance, just allow one.
    'ConformanceTypes':('Via Inputs','Via Model Mods', 'Via Combination'),

    # types of modification
    'ModificationTypes':('ModelMod','InputMod'),
    # input requirements
    'InputTypes':('InitialCondition','BoundaryCondition','AncillaryFile'),
    # model modification types
    'ModelModTypes':('ParameterChange','CodeChange'),

    # types of numerical requirement 
    'NumReqTypes':('BoundaryCondition','InitialCondition'),

    #ensembleTypes
    'EnsembleTypes':('Differing Start Date','Differing Initialisation','Perturbed Physics'),
    }

def reloadVocab(key):
    ''' Used to reset vocabulariews '''
    vocab=Vocab.objects.get(name=key)
    for v in Value.objects.filter(vocab=vocab):
        v.delete()
    vocab.delete()
    loadvocab(key)

def loadvocab(key):
    ''' Used to load vocabularies '''
    
    v=Vocab(uri=str(uuid.uuid1()),name=key)
    v.save()
    values=VocabList[key]
    for r in values:
        rv=Value(vocab=v,value=r)
        rv.save()

def initialise():
    '''This routine initialises the CMIP5 questionaire '''
    
    #start with initialising the centres:
    for centre in centres:
        u=str(uuid.uuid1())
        c=Centre(abbrev=centre[0],name=centre[1],uri=u)
        c.save()
        #and give each of them an unknown user to play with
        rp=ResponsibleParty(name='Unknown',abbrev='Unknown',address='Erehwon',email='u@foo.bar',
                            uri=str(uuid.uuid1()),centre=c)
        rp.save()
            
    for k in VocabList: loadvocab(k)