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
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/Numerics/$','cmip5q.protoq.views.componentNum'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/coupling/$','cmip5q.protoq.views.componentCup'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/Outputs/$','cmip5q.protoq.views.componentOut'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/Inputs/$','cmip5q.protoq.views.componentInp'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/copy/$','cmip5q.protoq.views.componentCopy'),
    #
    # REFERENCES (now handled in base view)
    #          
    #(r'^cmip5/(?P<centre_id>\d+)/references/$','cmip5q.protoq.views.referenceList'),
    #(r'^cmip5/(?P<centre_id>\d+)/reference/(?P<reference_id>\d+)/$','cmip5q.protoq.views.referenceEdit'),
    #(r'^cmip5/(?P<centre_id>\d+)/reference/$','cmip5q.protoq.views.referenceEdit'),  
    #(r'^cmip5/(?P<centre_id>\d+)/assignRefs/(?P<resourceType>\D+)/(?P<resource_id>\d+)/$',
    #        'cmip5q.protoq.views.assignReferences'),
    #
    # SIMULATIONS
    #
    (r'^cmip5/(?P<centre_id>\d+)/simulation/list/$',
                'cmip5q.protoq.views.simulationList'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/add/(?P<experiment_id>\d+)/$',
                'cmip5q.protoq.views.simulationAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/edit/$',
                'cmip5q.protoq.views.simulationEdit'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/validate/$',
                'cmip5q.protoq.views.simulationValidate'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/view/$',
                'cmip5q.protoq.views.simulationView'), 
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/$',
                'cmip5q.protoq.views.simulationCup'), 
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/(?P<coupling_id>\d+)/(?P<ctype>\D+)/$',
                'cmip5q.protoq.views.simulationCup'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/conformance/$',
                'cmip5q.protoq.views.conformanceMain'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/copy/$',
                'cmip5q.protoq.views.simulationCopy'),                     
    #           
    # platforms/add/centre_id
    # platforms/edit/platform_id
    #
    (r'^cmip5/(?P<centre_id>\d+)/platform/add$',
            'cmip5q.protoq.views.platformEdit'),
    (r'^cmip5/(?P<centre_id>\d+)/platform/(?P<platform_id>\d+)/edit$',
            'cmip5q.protoq.views.platformEdit'),
    #
    # experiment/view/experiment_id
    (r'^cmip5/(?P<cen_id>\d+)/experiment/(?P<experiment_id>\d+)/$',
            'cmip5q.protoq.views.viewExperiment'),   
                
    # cmip5/conformance/centre_id/simulation_id/requirement_id/$
    (r'^cmip5/conformance/(?P<cen_id>\d+)/(?P<sim_id>\d+)/(?P<req_id>\d+)/$',
            'cmip5q.protoq.views.conformanceEdit'),  
                     
    # help, intro, about
    (r'^cmip5/(?P<cen_id>\d+)/help/$',
            'cmip5q.protoq.views.help'),                  
    (r'^cmip5/(?P<cen_id>\d+)/about/$',
            'cmip5q.protoq.views.about'),     
    (r'^cmip5/(?P<cen_id>\d+)/intro/$',
            'cmip5q.protoq.views.intro'),                       
    # ensembles ...
    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/$',
            'cmip5q.protoq.views.ensemble'),
    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/(?P<ens_id>\d+)/$',
            'cmip5q.protoq.views.ensemble'),                                               
                          
    #### generic simple views
    # DELETE
    (r'^cmip5/(?P<cen_id>\d+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$',
            'cmip5q.protoq.views.delete'),
    (r'^cmip5/(?P<cen_id>\d+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$',
            'cmip5q.protoq.views.delete'),      
    # EDIT
    # cmip5q/centre_id/edit/resourceType/resourceID/returnType  (resourceID=0, blank form)
    (r'^cmip5/(?P<cen_id>\d+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$',
            'cmip5q.protoq.views.edit'),
    # cmip5q/centre_id/edit/resourceType/resourceID/targetType/targetID/returnType  
        #(resourceID=0, blank form)
    (r'^cmip5/(?P<cen_id>\d+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$',
            'cmip5q.protoq.views.edit'),
    # LIST
    (r'^cmip5/(?P<cen_id>\d+)/list/(?P<resourceType>\D+)/$',
            'cmip5q.protoq.views.list'),
    (r'^cmip5/(?P<cen_id>\d+)/list/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)$',
            'cmip5q.protoq.views.list'),
    # ASSIGN            
    (r'^cmip5/(?P<cen_id>\d+)/assign/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)/$',
            'cmip5q.protoq.views.assign'),       

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
