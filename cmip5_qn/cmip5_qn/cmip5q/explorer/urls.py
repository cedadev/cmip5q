from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # AR5 Tables Main Page:
    (r'^ar5/home/$', 'cmip5q.explorer.views_ar5.home'),
    (r'^ar5/modeldesc/$', 'cmip5q.explorer.views_ar5.modeldesc'),
    (r'^ar5/expdesign/$', 'cmip5q.explorer.views_ar5.expdesign'),
    (r'^ar5/modelforcing/$', 'cmip5q.explorer.views_ar5.modelforcing'),

    # model description csv and bibliography links
    (r'^ar5/modeldesc/csv/$', 'cmip5q.explorer.views_ar5.ar5csv'),
    (r'^ar5/modeldesc/bib/$', 'cmip5q.explorer.views_ar5.ar5bib'),

    # Strat Tables Main Page:
    (r'^strat/home/$', 'cmip5q.explorer.views_strat.home'),
    (r'^strat/modeldesc/$', 'cmip5q.explorer.views_strat.modeldesc'),

    # strat description csv and bibliography links
    (r'^strat/modeldesc/csv/$', 'cmip5q.explorer.views_strat.stratcsv'),
    (r'^strat/modeldesc/bib/$', 'cmip5q.explorer.views_strat.stratbib'),

    )
