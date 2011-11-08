from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #
    # AR5 Tables Main Page:
    #
    (r'^cmip5/ar5tables/$', 'cmip5q.ar5tables.views.ar5tables'),  
    (r'^cmip5/ar5csv/$', 'cmip5q.ar5tables.views.ar5csv'),
            
    )

