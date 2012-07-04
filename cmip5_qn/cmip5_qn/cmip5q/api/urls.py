from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #
    # Questionnaire API :
    #
    (r'^numdocs$','cmip5q.api.views.numdocs'),
                
    )

