from cmip5q.protoq.models import *
import uuid
CENTRES=(
             ('NCAS','UK National Centre for Atmospheric Science',('HiGEM1.2')),
             ('NCAR','US National Centre for Atmospheric Research',('CCSM4(H)','CCM4(M)')),
             ('MOHC','UK Met Office Hadley Centre',('HadCM3','HadCM3Q','HadGEM2-ES')),
             ('GFDL','Geophysical Fluid Dynamics Laboratory',('GFDL-HIRAM','GFDL-ESM2G','GFDL-ESM2M','GFDL-CM3','GFDL-CM2.1')),
             ('IPSL','Institut Pierre Simon Laplace',('IPSL-CM6','IPSL-CM5')),
             ('MPI-M','Max Planck Institute for Meteorology',('ECHAM5-MPIOM')), 
             ('CMIP5','Dummy Centre used to hold model template',('dum')),
             ('Example','Dummy Centre used to hold examples',('dum')),
             ('NorClim','Norwegian Climate Centre',('NorESM')),
             ('MRI','Japanese Meteorological Institute',('MRI-CGM3','MRI-ESM1','MRI-AM20km','MRI-AM60km')),
             ('MIROC','University of Tokyo, National Institute for Environmental Studies, and Japan Agency for Marine-Earth Science and Technology',('MIROC4.2(M)','(MIRO4.2(H)','MIROC3.2(M)','MIROC-ESM')),
             ('INM','Russian Institute for Numerical Mathematics',('INMCM4.0')),
             ('NIMR','Korean Naitonal Institute for Meteorological Research',('HadGEM2-AO')),
             ('LASG','Institute of Atmospheric Physics, Chinese Academy of Sciences	China',
                     ('FGOALS-S2.0','FGOALS-G2.0','FGOALS-gl')),
             ('QCCCE-CSIRO','Queensland Climate Change Centre of Excellence and Commonwealth Scientific and Industrial Research Organisation',('CSIRO-Mk3.5A')),
             ('CNRM/CERFACS','...',('CNRM-CM5')),
             ('CCCMA','Canadian Centre for Climate Modelling and Analysis',('CanESM2')),
             ('CAWCR','...	Australia',('ACCESS',)),
             ('CMA-BCC','Beijing Climate Center, China Meteorological Administration',('BCC-CSM'))
        )
def loadCentres():
    for centre in CENTRES:
        u=str(uuid.uuid1())
        c=Centre(abbrev=centre[0],name=centre[1],uri=u)
        c.save()
        #and give each of them an unknown user to play with
        rp=ResponsibleParty(name='Unknown',abbrev='Unknown',address='Erehwon',email='u@foo.bar',
                            uri=str(uuid.uuid1()),centre=c)
        rp.save()