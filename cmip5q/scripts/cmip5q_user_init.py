# Create cmip5q users
# Easiest to run this via "python manage.py shell"

from django.contrib.auth.models import User, Group


# Modelling centre norclim
q_norclim, created = Group.objects.get_or_create(name="cmip5q_norclim")
user, created = User.objects.get_or_create(username="jtjiputra",
    first_name="Jerry",
    last_name="Tjiputra",
    email="jtj061@bjerknes.uib.no",
    is_active=True)
user.groups.add(q_norclim)
user, created = User.objects.get_or_create(username="akirkevag",
    first_name="Alf",
    last_name="Kirkevag",
    email="alf.kirkevag@met.no",
    is_active=True)
user.groups.add(q_norclim)
user, created = User.objects.get_or_create(username="jdebernard",
    first_name="Jens",
    last_name="Debernard",
    email="jens.debernard@met.no",
    is_active=True)
user.groups.add(q_norclim)

# Modelling centre all
q_all, created = Group.objects.get_or_create(name="cmip5q_all")
user, created = User.objects.get_or_create(username="davidhassell",
    first_name="David",
    last_name="Hassell",
    email="d.c.hassell@reading.ac.uk",
    is_active=True)
user.groups.add(q_all)
user, created = User.objects.get_or_create(username="spascoe",
    first_name="Stephen",
    last_name="Pascoe",
    email="Stephen.Pascoe@stfc.ac.uk",
    is_active=True)
user.groups.add(q_all)

# Modelling centre nasagiss
q_nasagiss, created = Group.objects.get_or_create(name="cmip5q_nasagiss")

# Modelling centre inpe
q_inpe, created = Group.objects.get_or_create(name="cmip5q_inpe")
user, created = User.objects.get_or_create(username="mcoutinho",
    first_name="Mariane",
    last_name="Coutinho",
    email="mariane.coutinho@inpe.br",
    is_active=True)
user.groups.add(q_inpe)
user, created = User.objects.get_or_create(username="pjkersha",
    first_name="Philip James",
    last_name="Kershaw",
    email="Philip.Kershaw@stfc.ac.uk",
    is_active=True)
user.groups.add(q_inpe)

# Modelling centre mpim
q_mpim, created = Group.objects.get_or_create(name="cmip5q_mpim")
user, created = User.objects.get_or_create(username="kfieg",
    first_name="Kerstin",
    last_name="Fieg",
    email="fieg@dkrz.de",
    is_active=True)
user.groups.add(q_mpim)
user, created = User.objects.get_or_create(username="hramthun",
    first_name="Hans",
    last_name="Ramthun",
    email="ramthun@dkrz.de",
    is_active=True)
user.groups.add(q_mpim)

# Modelling centre inm
q_inm, created = Group.objects.get_or_create(name="cmip5q_inm")

# Modelling centre ncep
q_ncep, created = Group.objects.get_or_create(name="cmip5q_ncep")
user, created = User.objects.get_or_create(username="ptripp",
    first_name="Patrick",
    last_name="Tripp",
    email="patrick.tripp@noaa.gov",
    is_active=True)
user.groups.add(q_ncep)

# Modelling centre mohc
q_mohc, created = Group.objects.get_or_create(name="cmip5q_mohc")
user, created = User.objects.get_or_create(username="allynt",
    first_name="Allyn",
    last_name="Treshansky",
    email="allyn.treshansky@noaa.gov",
    is_active=True)
user.groups.add(q_mohc)
user, created = User.objects.get_or_create(username="reade",
    first_name="Rosemary",
    last_name="Eade",
    email="rosie.eade@metoffice.gov.uk",
    is_active=True)
user.groups.add(q_mohc)
user, created = User.objects.get_or_create(username="mohc_review",
    first_name="mohc_review",
    last_name="mohc_review",
    email="mark.elkington@metoffice.gov.uk",
    is_active=True)
user.groups.add(q_mohc)
user, created = User.objects.get_or_create(username="melkington",
    first_name="Mark",
    last_name="Elkington",
    email="mark.elkington@metoffice.gov.uk",
    is_active=True)
user.groups.add(q_mohc)

# Modelling centre gcess
q_gcess, created = Group.objects.get_or_create(name="cmip5q_gcess")
user, created = User.objects.get_or_create(username="jidy",
    first_name="Duoying",
    last_name="Ji",
    email="duoyingji@bnu.edu.cn",
    is_active=True)
user.groups.add(q_gcess)

# Modelling centre nasagmao
q_nasagmao, created = Group.objects.get_or_create(name="cmip5q_nasagmao")

# Modelling centre cnrm_cerfacs
q_cnrm_cerfacs, created = Group.objects.get_or_create(name="cmip5q_cnrm_cerfacs")
user, created = User.objects.get_or_create(username="svalcke",
    first_name="Sophie",
    last_name="Valcke",
    email="valcke@cerfacs.fr",
    is_active=True)
user.groups.add(q_cnrm_cerfacs)

# Modelling centre nimr
q_nimr, created = Group.objects.get_or_create(name="cmip5q_nimr")

# Modelling centre fio
q_fio, created = Group.objects.get_or_create(name="cmip5q_fio")

# Modelling centre cmabcc
q_cmabcc, created = Group.objects.get_or_create(name="cmip5q_cmabcc")

# Modelling centre rsmas
q_rsmas, created = Group.objects.get_or_create(name="cmip5q_rsmas")

# Modelling centre utnies
q_utnies, created = Group.objects.get_or_create(name="cmip5q_utnies")

# Modelling centre ecearth
q_ecearth, created = Group.objects.get_or_create(name="cmip5q_ecearth")
user, created = User.objects.get_or_create(username="hardenberg",
    first_name="Jost",
    last_name="von Hardenberg",
    email="j.vonhardenberg@isac.cnr.it",
    is_active=True)
user.groups.add(q_ecearth)

# Modelling centre ipsl
q_ipsl, created = Group.objects.get_or_create(name="cmip5q_ipsl")
user, created = User.objects.get_or_create(username="sdenvil",
    first_name="Sebastien",
    last_name="Denvil",
    email="sebastien.denvil@ipsl.jussieu.fr",
    is_active=True)
user.groups.add(q_ipsl)

# Modelling centre admin
q_admin, created = Group.objects.get_or_create(name="cmip5q_admin")

# Modelling centre cccma
q_cccma, created = Group.objects.get_or_create(name="cmip5q_cccma")

# Modelling centre ccsm
q_ccsm, created = Group.objects.get_or_create(name="cmip5q_ccsm")
user, created = User.objects.get_or_create(username="southern",
    first_name="Lawrence",
    last_name="Buja",
    email="southern@ucar.edu",
    is_active=True)
user.groups.add(q_ccsm)
user, created = User.objects.get_or_create(username="trey",
    first_name="James",
    last_name="White",
    email="trey@ucar.edu",
    is_active=True)
user.groups.add(q_ccsm)

# Modelling centre cawcr
q_cawcr, created = Group.objects.get_or_create(name="cmip5q_cawcr")
user, created = User.objects.get_or_create(username="pfu599",
    first_name="Peter",
    last_name="Uhe",
    email="Peter.Uhe@csiro.au",
    is_active=True)
user.groups.add(q_cawcr)
user, created = User.objects.get_or_create(username="achirst",
    first_name="Anthony Churchill",
    last_name="Hirst",
    email="tony.hirst@csiro.au",
    is_active=True)
user.groups.add(q_cawcr)

# Modelling centre mri
q_mri, created = Group.objects.get_or_create(name="cmip5q_mri")
user, created = User.objects.get_or_create(username="rmizuta",
    first_name="Ryo",
    last_name="Mizuta",
    email="rmizuta@mri-jma.go.jp",
    is_active=True)
user.groups.add(q_mri)

# Modelling centre lasg
q_lasg, created = Group.objects.get_or_create(name="cmip5q_lasg")
user, created = User.objects.get_or_create(username="shanshan",
    first_name="shanshan",
    last_name="Hou",
    email="rs_houshanshan@126.com",
    is_active=True)
user.groups.add(q_lasg)
user, created = User.objects.get_or_create(username="llijuan",
    first_name="Li",
    last_name="Lijuan",
    email="ljli@mail.iap.ac.cn",
    is_active=True)
user.groups.add(q_lasg)

# Modelling centre ncar
q_ncar, created = Group.objects.get_or_create(name="cmip5q_ncar")
user, created = User.objects.get_or_create(username="allynt",
    first_name="Allyn",
    last_name="Treshansky",
    email="allyn.treshansky@noaa.gov",
    is_active=True)
user.groups.add(q_ncar)
user, created = User.objects.get_or_create(username="southern",
    first_name="Lawrence",
    last_name="Buja",
    email="southern@ucar.edu",
    is_active=True)
user.groups.add(q_ncar)

# Modelling centre ncas
q_ncas, created = Group.objects.get_or_create(name="cmip5q_ncas")

# Modelling centre csiro
q_csiro, created = Group.objects.get_or_create(name="cmip5q_csiro")

# Modelling centre cmcc
q_cmcc, created = Group.objects.get_or_create(name="cmip5q_cmcc")
user, created = User.objects.get_or_create(username="sgualdi01",
    first_name="Silvio",
    last_name="Gualdi",
    email="silvio.gualdi@bo.ingv.it",
    is_active=True)
user.groups.add(q_cmcc)

# Modelling centre gfdl
q_gfdl, created = Group.objects.get_or_create(name="cmip5q_gfdl")
user, created = User.objects.get_or_create(username="allynt",
    first_name="Allyn",
    last_name="Treshansky",
    email="allyn.treshansky@noaa.gov",
    is_active=True)
user.groups.add(q_gfdl)
user, created = User.objects.get_or_create(username="rgudgel",
    first_name="Richard",
    last_name="Gudgel",
    email="rich.gudgel@noaa.gov",
    is_active=True)
user.groups.add(q_gfdl)
user, created = User.objects.get_or_create(username="krasting",
    first_name="John",
    last_name="Krasting",
    email="John.Krasting@noaa.gov",
    is_active=True)
user.groups.add(q_gfdl)
user, created = User.objects.get_or_create(username="lsentman",
    first_name="Lori",
    last_name="Sentman",
    email="Lori.Sentman@noaa.gov",
    is_active=True)
user.groups.add(q_gfdl)
user, created = User.objects.get_or_create(username="kolivo",
    first_name="Kyle",
    last_name="Olivo",
    email="kyle.olivo@noaa.gov",
    is_active=True)
user.groups.add(q_gfdl)

