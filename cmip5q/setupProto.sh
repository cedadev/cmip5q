source ~/meta4q/bin/activate


#This only works if you use sqlite of course ...
rm sqlite.db

#for now we don't have a superuser, which means no admin
python manage.py syncdb <<EOF
no
EOF

python manage.py shell << EOF
#
# set up some things after a complete database rewriet
#
from protoq.models import *
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
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM PreInd Con',title='ESM pre-industrial control',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM hist',title='ESM historical',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM RCP8.5',title='ESM RCP8.5',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM fixed 1',title='ESM fixed climate 1',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM fixed 2',title='ESM fixed climate 2',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM feedback 1',title='ESM feedback climate 1',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='ESM feedback 2',title='ESM feedback climate 2',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='1% CO2',title='1 percent per year CO2',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='SST cont',title='control SST climatology',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='CO2 Forcing',title='CO2 Forcing',uri=u)
e.save()
u=str(uuid.uuid1())
e=Experiment(abbrev='4xCO2  Abrupt',title='4XCO2 Abrupt Forcing',uri=u)
e.save()

EOF
