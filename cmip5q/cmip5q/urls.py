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
    (r'^cmip5/(?P<centre_id>\d+)/$','cmip5q.protoq.views.centre'),
    # 
    # COMPONENTS:
    #   
    (r'^cmip5/(?P<centre_id>\d+)/component/add/$','cmip5q.protoq.views.componentAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/edit/$','cmip5q.protoq.views.componentEdit'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/addsub/$','cmip5q.protoq.views.componentSub'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/refs/$','cmip5q.protoq.views.componentRefs'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/validate/$','cmip5q.protoq.views.componentValidate'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/view/$','cmip5q.protoq.views.componentView'),   
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/XML/$','cmip5q.protoq.views.componentXML'),   
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
    # SIMULATIONS
    #
    (r'^cmip5/(?P<centre_id>\d+)/simulation/list/$',
                'cmip5q.protoq.views.simulationList'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/add/(?P<experiment_id>\d+)/$',
                'cmip5q.protoq.views.simulationAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/edit/$',
                'cmip5q.protoq.views.simulationEdit'),  
                    
    #           
    # platforms/add/centre_id
    # platforms/edit/platform_id
    #
    (r'^cmip5/(?P<centre_id>\d+)/platform/add$',
            'cmip5q.protoq.views.platformAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/platform/(?P<platform_id>\d+)/edit$',
            'cmip5q.protoq.views.platformEdit'),
    #
    # experiment/experiment_id
    (r'^cmip5/experiment/view/(?P<experiment_id>\d+)/$',
            'cmip5q.protoq.views.viewExperiment'),   
                
    # cmip5/conformance/centre_id/simulation_id/requirement_id/$
    (r'^cmip5/conformance/(?P<cen_id>\d+)/(?P<sim_id>\d+)/(?P<req_id>\d+)/$',
            'cmip5q.protoq.views.conformanceEdit'),      
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