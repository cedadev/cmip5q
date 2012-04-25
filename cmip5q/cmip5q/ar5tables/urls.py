from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # AR5 Tables Main Page:
    (r'^ar5/overview/$', 'cmip5q.explorer.views.ar5overview'),
    (r'^ar5/modeldesc/$', 'cmip5q.explorer.views.ar5modeldesc'),
    (r'^ar5/expdesign/$', 'cmip5q.explorer.views.ar5expdesign'),
    (r'^ar5/modelforcing/$', 'cmip5q.explorer.views.ar5modelforcing'),
      
    # model description csv and bibliography links
    (r'^ar5/modeldesc/csv/$', 'cmip5q.explorer.views.ar5csv'),
    (r'^ar5/modeldesc/bib/$', 'cmip5q.explorer.views.ar5bib'),
    
    # Strat Tables Main Page:
    (r'^strat/overview/$', 'cmip5q.explorer.views.stratoverview'),
    (r'^strat/modeldesc/$', 'cmip5q.explorer.views.stratmodeldesc'),
            
    )

