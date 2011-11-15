from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #
    # Questionnaire API :
    #
    (r'^cmip5/api/(?P<docType>\D+)/$','cmip5q.api.views.numdocs'),
                
    )

