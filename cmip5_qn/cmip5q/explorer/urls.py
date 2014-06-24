from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #--------------------------------------------------------------------------
    # AR5 Tables Main Page:
    (r'^ar5/$', 'cmip5q.explorer.views_ar5.home'),
    (r'^ar5/modeldesc/$', 'cmip5q.explorer.views_ar5.create_modeldesc'),
    (r'^ar5/expdesign/$', 'cmip5q.explorer.views_ar5.expdesign'),
    (r'^ar5/modelforcing/$', 'cmip5q.explorer.views_ar5.modelforcing'),
    (r'^ar5/ch09/$', 'cmip5q.explorer.views_ar5.create_ch09table'),
    (r'^ar5/chem/$', 'cmip5q.explorer.views_ar5.chem'),

    # model description csv and bibliography links
    (r'^ar5/modeldesc/csv/$', 'cmip5q.explorer.views_ar5.ar5csv'),
    (r'^ar5/modeldesc/bib/$', 'cmip5q.explorer.views_ar5.ar5bib'),
    (r'^ar5/ch09/csv/$', 'cmip5q.explorer.views_ar5.ch09csv'),
    (r'^ar5/ch09/bib/$', 'cmip5q.explorer.views_ar5.ch09bib'),
    (r'^ar5/chem/csv/$', 'cmip5q.explorer.views_ar5.chemcsv'),
    
    
    #--------------------------------------------------------------------------
    # Strat Tables Main Page:
    (r'^strat/$', 'cmip5q.explorer.views_strat.home'),
    (r'^strat/home/$', 'cmip5q.explorer.views_strat.home'),
    (r'^strat/modeldesc/$', 'cmip5q.explorer.views_strat.modeldesc'),

    # strat description csv and bibliography links
    (r'^strat/modeldesc/csv/$', 'cmip5q.explorer.views_strat.stratcsv'),
    (r'^strat/modeldesc/bib/$', 'cmip5q.explorer.views_strat.stratbib'),
    
    )