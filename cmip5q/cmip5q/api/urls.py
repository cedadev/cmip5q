from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #
    # Questionnaire API :
    #
    (r'^cmip5/api/numdocs$','cmip5q.api.views.numdocs'),
                
    )

