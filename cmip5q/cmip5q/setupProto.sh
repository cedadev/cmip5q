# comment out the following line for deployment
source ~/meta4q/bin/activate

# This only works if you use sqlite of course ...
rm -f sqlite.db

# for now we don't have a superuser, which means no admin
${PYTHON:-python} manage.py syncdb <<EOF
no
EOF

# set up some things after a complete database rewrite
${PYTHON:-python} manage.py shell << EOF

from protoq.models import *
from XMLinitialiseQ import initialise
from XMLActivityReader import NumericalExperiment
from initialiseRefs import *
from initialiseFiles import *

# Initialise the Questionnaire
initialise()

# load cmip5 input files
initialiseFiles()

# load cmip5 input references
initialiseRefs()

# create experiments

import os
experimentDir = './data/experiments'
for f in os.listdir(experimentDir):
    if f.endswith('.xml'):
	    x=NumericalExperiment(os.path.join(experimentDir, f)) 
	    x.load()

EOF
