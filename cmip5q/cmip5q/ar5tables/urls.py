from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # AR5 Tables Main Page:
    (r'^overview/$', 'cmip5q.ar5tables.views.overview'),
    (r'^modeldesc/$', 'cmip5q.ar5tables.views.modeldesc'),
    (r'^expdesign/$', 'cmip5q.ar5tables.views.expdesign'),
    (r'^modelforcing/$', 'cmip5q.ar5tables.views.modelforcing'),
      
    # model description csv and bibliography links
    (r'^modeldesc/csv/$', 'cmip5q.ar5tables.views.ar5csv'),
    (r'^modeldesc/bib/$', 'cmip5q.ar5tables.views.ar5bib'),
            
    )

