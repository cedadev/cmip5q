
import os

# get the cmip5 settings
os.environ['DJANGO_SETTINGS_MODULE']='settings'

from protoq.models import *
from XMLinitialiseQ import initialise
from XMLActivityReader import NumericalExperiment
from NumericalModel import *
from initialiseRefs import *
from initialiseFiles import *
from initialiseVars import *

# Initialise the Questionnaire
initialise()

# load cmip5 input files
initialiseFiles()

# load variables associated with cmip5 input files
initialiseVars()

# load cmip5 input references
initialiseRefs()

# create experiments

experimentDir = './data/experiments'
for f in os.listdir(experimentDir):
    if f.endswith('.xml'):
	    x=NumericalExperiment(os.path.join(experimentDir, f)) 
	    x.load()

# initialise a model template
initialiseModel()
