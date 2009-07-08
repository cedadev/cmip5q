#source ~/meta4q/bin/activate


# This only works if you use sqlite of course ...
rm -f sqlite.db

# for now we don't have a superuser, which means no admin
${PYTHON:-python} manage.py syncdb <<EOF
no
EOF

${PYTHON:-python} manage.py shell << EOF
#
# set up some things after a complete database rewrite
#
from protoq.models import *
from XMLActivityReader import NumericalExperiment
import uuid

#
# create a couple of centres
#
u=str(uuid.uuid1())
c=Centre(abbrev='MOHC',title="Met Office Hadley Centre",uri=u)
c.save()
u=str(uuid.uuid1())
c=Centre(abbrev='NCAS',title="NCAS Climate HIGEM Project",uri=u)
c.save()

#
# create a couple of experiments
#
for f in ['1.6_Decadal_AtmosChem.xml']:
    x=NumericalExperiment(f) 
    x.load()
    

EOF
