
from django.core.management import setup_environ
import settings
setup_environ(settings)

from NumericalModel import *
from XMLActivityReader import *
from cf import *

if __name__=="__main__":
   
    unittest.main()