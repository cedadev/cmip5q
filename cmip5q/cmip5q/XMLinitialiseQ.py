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

def initialise():
    '''This routine initialises the CMIP5 questionaire '''
    
    #start with initialising the centres:
    for centre in centres:
        u=str(uuid.uuid1())
        c=Centre(abbrev=centre[0],title=centre[1],uri=u)
        c.save()
        
    #now add reference type vocabulary
    v=Vocab(uri=str(uuid.uuid1()),name='Reference Types Vocab')
    v.save()
    for r in referenceTypes:
        rv=Value(vocab=v,value=r)
        rv.save()
    