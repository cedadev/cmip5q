from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # AR5 Tables Main Page:
    (r'^cmip5/explorer/ar5/overview/$', 'cmip5q.ar5tables.views.overview'),
    (r'^cmip5/explorer/ar5/modeldesc/$', 'cmip5q.ar5tables.views.modeldesc'),
    (r'^cmip5/explorer/ar5/expdesign/$', 'cmip5q.ar5tables.views.expdesign'),
    (r'^cmip5/explorer/ar5/modelforcing/$', 'cmip5q.ar5tables.views.modelforcing'),
      
    # model description csv and bibliography links
    (r'^cmip5/explorer/ar5/modeldesc/csv/$', 'cmip5q.ar5tables.views.ar5csv'),
    (r'^cmip5/explorer/ar5/modeldesc/bib/$', 'cmip5q.ar5tables.views.ar5bib'),
            
    )

