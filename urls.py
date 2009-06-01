from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^cmip5q/', include('cmip5q.foo.urls')),
    (r'^$','cmip5q.protoq.views.centres'),
    (r'^cmip5/$','cmip5q.protoq.views.centres'),
    (r'^cmip5/centres/$','cmip5q.protoq.views.centres'),
    (r'^cmip5/centre/(?P<centre_id>\d+)/$','cmip5q.protoq.views.centre'),
    # 
    # components/add/centre_id/
    # components/add/centre_id/component_type|component_id/  (the latter for copy as new)
    # components/edit/component_id
    # components/edit/component_id/parent_id/
    # components/addsub/parent_id/
    # components/addsub/parent_id/component_type|component_id/ (the latter for copy as new)
    # components/list/centre_id
    #   
    (r'^cmip5/components/add/(?P<centre_id>\d+)/$','cmip5q.protoq.views.addComponent'),
    (r'^cmip5/components/edit/(?P<component_id>\d+)/$','cmip5q.protoq.views.editComponent'),
    (r'^cmip5/components/addsub/(?P<parent_id>\d+)/$','cmip5q.protoq.views.addSubComponent'),
    (r'^cmip5/components/list/(?P<centre_id>\d+)/$','cmip5q.protoq.views.listComponents'),
    (r'^cmip5/components/addrefs/(?P<component_id>\d+)/$','cmip5q.protoq.views.componentRefs'),
    (r'^cmip5/components/addsubs/(?P<component_id>\d+)/$','cmip5q.protoq.views.componentSubs'),
    (r'^cmip5/components/assign/(?P<component_id>\d+)/(?P<sub_id>\d+)/$','cmip5q.protoq.views.assignComponent'),
    #
    # references
    # reference/add    
    #          
    (r'^cmip5/references/$','cmip5q.protoq.views.references'),
    (r'^cmip5/references/add/$','cmip5q.protoq.views.addReference'),
    (r'^cmip5/references/add/(?P<component_id>\d+)/$','cmip5q.protoq.views.addReference'),
    (r'^cmip5/references/edit/(?P<reference_id>\d+)/$','cmip5q.protoq.views.editReference'),
    (r'^cmip5/references/assign/(?P<component_id>\d+)/(?P<reference_id>\d+)/$','cmip5q.protoq.views.assignReference'),
    (r'^cmip5/references/remove/(?P<component_id>\d+)/(?P<reference_id>\d+)/$','cmip5q.protoq.views.remReference'),
    #
    # simulations/add/centre_id/experiment_id/
    # simulations/list/centre_id/experiment_id/
    # simulations/edit/simulation_id/
    #
    (r'^cmip5/simulations/add/(?P<centre_id>\d+)/(?P<experiment_id>\d+)/$',
                'cmip5q.protoq.views.addSimulation'),
    (r'^cmip5/simulations/edit/(?P<simulation_id>\d+)/$',
                'cmip5q.protoq.views.editSimulation'),
    (r'^cmip5/simulations/list/(?P<centre_id>\d+)/(?P<experiment_id>\d+)/$',
                'cmip5q.protoq.views.listSimulations'),
    #
    # platforms/add/centre_id
    # platforms/edit/platform_id
    #
    (r'^cmip5/platforms/add/(?P<centre_id>\d+)/$',
            'cmip5q.protoq.views.addPlatform'),
    (r'^cmip5/platforms/edit/(?P<platform_id>\d+)/$',
            'cmip5q.protoq.views.editPlatform'),
    #
    # experiment/experiment_id
    (r'^cmip5/experiment/view/(?P<experiment_id>\d+)/$',
            'cmip5q.protoq.views.viewExperiment'),   
    #
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_DOC_ROOT,'show_indexes': True}),
    )
