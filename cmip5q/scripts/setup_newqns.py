'''
Miscellaneous script to set up infrastructure for new cmip5 questions
'''

import os
import sys

# putting project and application into sys.path
sys.path.append('../cmip5q')
sys.path.append('../cmip5q/protoq')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmip5q.settings'
from django.core.management import setup_environ
from cmip5q import settings
setup_environ(settings)

from cmip5q.protoq.models import *


# Dictionary representation of new questions
newqns = [
          {"paramgroup": u"Model development path", 
           "paramsets":
            [
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"ModelAssembly",
                 "paramdef": u"Would you qualify that your CMIP5 model is:",
                 "paramtype": u"XOR",
                 "paramvalues": [u"Assembled from components mostly developed in your institution", 
                                 u"Assembled from components mostly developed in other institutions",
                                 u"Developed as part of a multi-institute formal consortium",
                                 u"Assembled from a mix of in house and other institutions components",
                                 u"Mostly taken off shelf from another institution"]
                },
                {"constraint": 'if ModelAssembly is "Assembled from components mostly developed in other institutions"',
                 "paramname": u"AssemblyOtherInstitutes",
                 "paramdef": u"Please list which other institutes form part of the model assembly",
                 "paramtype": u"keyboard"
                },
                {"constraint": 'if ModelAssembly is "Developed as part of a multi-institute formal consortium"',
                 "paramname": u"AssemblyConsortium",
                 "paramdef": u"Please state name of the multi-institute consortium name",
                 "paramtype": u"keyboard"
                },
                {"constraint": 'if ModelAssembly is "Assembled from a mix of in house and other institutions components"',
                 "paramname": u"MixedAssemblyNames",
                 "paramdef": u"Please list which components and which institutions were involved in the model assembly",
                 "paramtype": u"keyboard"
                },
                {"constraint": 'if ModelAssembly is "Mostly taken off shelf from another institution"',
                 "paramname": u"OffShelfInst",
                 "paramdef": u"Please list which off-the-shelf institution",
                 "paramtype": u"keyboard"
                },
              ]
             #------------------------------------------------------
            ]
          },
          
          #====================================================================
          #====================================================================
          
          {"paramgroup": u"Tuning Section", 
           "paramsets":
            [
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"MeanStateGlobalMetrics",
                 "paramdef": u"What global metrics of the mean state are specifically used in the model tuning process?",              
                 "paramtype": u"OR",
                 "paramvalues": [u"Global mean TOA net flux", 
                                 u"Global mean surface net flux",
                                 u"Global mean planetary albedo",
                                 u"Global mean surface albedo",
                                 u"Global mean OLR",
                                 u"Global mean surface temperature",
                                 u"Other: please specify"]
                 },
              ],
             #------------------------------------------------------
              [
             
                {"constraint": "",
                 "paramname": u"ObservedTrendsMetrics",
                 "paramdef": u"What metrics of observed trends are specifically used in the model tuning process?",
                 "paramtype": u"OR",
                 "paramvalues": [u"Global mean surface temperature", 
                                 u"Aerosols ",
                                 u"Other: please specify",
                                 u"None"]
                 },
              ],
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"MeanStateRegionalMetrics",
                 "paramdef": u"What regional metrics of the mean state are specifically used in the model tuning process?",
                 "paramtype": u"OR",
                 "paramvalues": [u"Meridional gradient in net TOA flux", 
                                 u"Tropical mean values",
                                 u"Monsoons ",
                                 u"Other: please specify",
                                 u"None"]
                 },
              ],
             #------------------------------------------------------
              [
             
                {"constraint": "",
                 "paramname": u"TemporalVariabilityMetrics",
                 "paramdef": u"What metrics of temporal variability are specifically used in the model tuning process? (do any groups tune to temporal variability?)",
                 "paramtype": u"OR",
                 "paramvalues": [u"ENSO-related", 
                                 u"Interannual variability",
                                 u"Volcanic responses",
                                 u"Other: please specify",
                                 u"None"]
                 },
              ],
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"AdjustedParameters",
                 "paramdef": u"What model parameters are subject to adjustment in your model tuning process?",
                 "paramtype": u"OR",
                 "paramvalues": [u"Cloud properties (e.g. drop size distribution,... please specify in free text area)", 
                                 u"RH threshold for condensate",
                                 u"Entrainment parameters",
                                 u"Sub-grid orographic drag parameters", 
                                 u"Conversion rates from cloud water/ice to rain/snow",
                                 u"Precipitating condensate fall velocities",
                                 u"Cloud inhomogeneity settings",
                                 u"Ocean albedo", 
                                 u"River run off location",
                                 u"Other: please list"]
                 },
              ],
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"OtherModelTuning?",
                 "paramdef": u"Anything else that you wish to document about model tuning?",
                 "paramtype": u"keyboard"             
                 }
              ]
             #------------------------------------------------------
            ] 
           },
          
          #==================================================================
          #==================================================================
                    
          {"paramgroup": u"Conservation of integral quantities", 
           "paramsets":
            [
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"IntegralConservation",
                 "paramdef": u"Was there any specific effort made to conserve any integral quantities (either globally or per component)?",
                 "paramtype": u"OR",
                 "paramvalues": [u"Energy", 
                                 u"Fresh water",
                                 u"Momentum",
                                 u"Other"]
                 }
              ],
             #------------------------------------------------------
              [
                {"constraint": "",
                 "paramname": u"SpecificTuning",
                 "paramdef": u"If applicable, describe any specific tuning/treatment done to ensure this conservation",
                 "paramtype": u"keyboard"
                }
              ],
             #------------------------------------------------------
              [              
                {"constraint": "",
                 "paramname": u"FluxCorrectionUsed",
                 "paramdef": u"Was a flux correction used?",
                 "paramtype": u"XOR",
                 "paramvalues": [u"Yes", u"No"]
                },
                {"constraint": 'if FluxCorrectionUsed is "Yes"',
                 "paramname": u"FluxCorrectionFields",
                 "paramdef": u"Which fields were used in the flux correction?",
                 "paramtype": u"OR",
                 "paramvalues": [u"Heat", u"Water Flux", u"Momentum"]
                },
                {"constraint": 'if FluxCorrectionUsed is "Yes"',
                 "paramname": u"FluxCorrectionMethod",
                 "paramdef": u"How was the flux correction implemented?",
                 "paramtype": u"keyboard"
                },
              ]
             #------------------------------------------------------
            
            ]
           },
         ]


#
# Script to feed this dictionary into the current database
# (runs a simple keyboard check first given this directly modifies the database)
# 

proceed = raw_input('Are you sure you want to run this (database-altering) script? (Y/N)')

if proceed == 'Y' or proceed =='y':
    # retrieve all non-deleted models
    models = Component.objects.filter(isDeleted=False).filter(isModel=True)
    
    for model in models:
        print 'Model = %s' % model.abbrev
        # loop over each set of questions and add to the top level component
        for qn in newqns:
            pg = ParamGroup(name=qn["paramgroup"])
            pg.save()
            model.paramGroup.add(pg)
            
            # these set of questions currently do not involve constraint groups so we 
            # can just set it to empty
            #cg = ConstraintGroup(constraint='', parentGroup=pg)
            #cg.save()
            
            for paramset in qn['paramsets']:
                for cgset in paramset:
                    cg = ConstraintGroup(constraint=cgset['constraint'], parentGroup=pg)
                    cg.save()    
                    # set up the specific param instance
                    paramName = cgset['paramname']
                    paramDef = cgset['paramdef']
                    choiceType = cgset['paramtype']
                    
                    Param={'OR':OrParam, 
                           'XOR':XorParam,
                           'keyboard':KeyBoardParam}[choiceType]
                           
                    if choiceType in ['OR','XOR']:
                        # remove any potential spaces from param names
                        paramName = paramName.replace(' ', '')
                        paramDef = paramDef
                        v = Vocab(uri=atomuri(), name=paramName+'Vocab')
                        v.save()
                        
                        for item in cgset['paramvalues']:
                            value = Term(vocab=v, name=item)
                            value.save()
                            
                        p = Param(name=paramName, 
                                  constraint=cg,
                                  vocab=v,
                                  definition=paramDef,
                                  controlled=True)
                        p.save()
                    
                    elif choiceType in ['keyboard']:        
                        p = Param(name=paramName,
                                constraint=cg,
                                definition=paramDef, 
                                units=None, 
                                numeric=False, 
                                controlled=True)
                        p.save()
    
    print 'Finished'
else:
    print 'exiting script without running'
    