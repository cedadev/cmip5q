# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from cmip5q.protoq.feeds import DocFeed

# this is not actually correct, since strictly we need hexadecimal following this pattern
uuid='\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w'

script_path=settings.DEPLOYED_SCRIPT_PATH

urlpatterns = patterns('',
    # Example:
    # (r'^cmip5q/', include('cmip5q.foo.urls')),
    (r'^$','cmip5q.protoq.views.centres'),
    (r'^cmip5/$','cmip5q.protoq.views.centres'),
    (r'^cmip5/centres/$','cmip5q.protoq.views.centres'),
    (r'^cmip5/(?P<centre_id>\d+)/$','cmip5q.protoq.views.centre'),
    # 
    url(r'^cmip5/authz/$','cmip5q.protoq.views.authorisation',name='security'),
    #        
    # ajax vocabulary handler
    url(r'^ajax/(?P<vocabName>\D+)/$','cmip5q.protoq.views.completionHelper',name='ajax_value'),
    #
    # generic document handling
    # 
    (r'^cmip5/(?P<cid>\d+)/(?P<docType>\D+)/doc/(?P<pkid>\d+)/(?P<method>\D+)/$','cmip5q.protoq.views.genericDoc'),  
    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/$'%uuid,'cmip5q.protoq.views.persistedDoc'),
    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/(?P<version>\d+)/$'%uuid,'cmip5q.protoq.views.persistedDoc'),                     
    # 
    # COMPONENTS:
    #   
    (r'^cmip5/(?P<centre_id>\d+)/component/add/$','cmip5q.protoq.views.componentAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/edit/$','cmip5q.protoq.views.componentEdit'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/addsub/$','cmip5q.protoq.views.componentSub'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/refs/$','cmip5q.protoq.views.componentRefs'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/coupling/$','cmip5q.protoq.views.componentCup'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/Inputs/$','cmip5q.protoq.views.componentInp'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/copy/$','cmip5q.protoq.views.componentCopy'),
    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/text/$','cmip5q.protoq.views.componentTxt'),
    #
    # SIMULATIONS
    #
    (r'^cmip5/(?P<centre_id>\d+)/simulation/list/$',
                'cmip5q.protoq.views.simulationList'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/add/(?P<experiment_id>\d+)/$',
                'cmip5q.protoq.views.simulationAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/edit/$',
                'cmip5q.protoq.views.simulationEdit'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/$',
                'cmip5q.protoq.views.simulationCup'), 
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/(?P<coupling_id>\d+)/(?P<ctype>\D+)/$',
                'cmip5q.protoq.views.simulationCup'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/conformance/$',
                'cmip5q.protoq.views.conformanceMain'),  
    (r'^cmip5/(?P<centre_id>\d+)/simulation/copy/$',
                'cmip5q.protoq.views.simulationCopy'),
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/copyind/$',
                'cmip5q.protoq.views.simulationCopyInd'),
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/resetCouplings/$',
                'cmip5q.protoq.views.simulationCupReset'), 
    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/delete/$',
                'cmip5q.protoq.views.simulationDel'),
    # 
    # GRIDS:
    #   
    (r'^cmip5/(?P<centre_id>\d+)/grid/add/$','cmip5q.protoq.views.gridAdd'),
    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/copy/$','cmip5q.protoq.views.gridCopy'),
    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/edit/$','cmip5q.protoq.views.gridEdit'),
    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/refs/$','cmip5q.protoq.views.gridRefs'),             
    #           
    # platforms/add/centre_id
    # platforms/edit/platform_id
    #
    (r'^cmip5/(?P<centre_id>\d+)/platform/add/$',
            'cmip5q.protoq.views.platformEdit'),
    (r'^cmip5/(?P<centre_id>\d+)/platform/(?P<platform_id>\d+)/edit/$',
            'cmip5q.protoq.views.platformEdit'),
    #
    # experiment/view/experiment_id
    (r'^cmip5/(?P<cen_id>\d+)/experiment/(?P<experiment_id>\d+)/$',
            'cmip5q.protoq.views.viewExperiment'),
    
    # cmip5/conformance/centre_id/simulation_id/requirement_id/$
    (r'^cmip5/conformance/(?P<cen_id>\d+)/(?P<sim_id>\d+)/(?P<req_id>\d+)/$',
            'cmip5q.protoq.views.conformanceEdit'),  
                     
    # help, intro, about, vn history
    (r'^cmip5/(?P<cen_id>\d+)/help/$',
            'cmip5q.protoq.views.help'),
    (r'^cmip5/(?P<cen_id>\d+)/vnhist/$',
            'cmip5q.protoq.views.vnhist'),
    (r'^cmip5/(?P<cen_id>\d+)/trans/$',
            'cmip5q.protoq.views.trans'),              
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
    (r'^cmip5/(?P<cen_id>\d+)/filterlist/(?P<resourceType>\D+)$',
            'cmip5q.protoq.views.filterlist'),
    # ASSIGN            
    (r'^cmip5/(?P<cen_id>\d+)/assign/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)/$',
            'cmip5q.protoq.views.assign'),       
            
    # export files to CMIP5
    (r'^cmip5/(?P<cen_id>\d+)/exportFiles/$','cmip5q.protoq.views.exportFiles'), 
    (r'^cmip5/testFile/(?P<fname>.+)$','cmip5q.protoq.views.testFile'),
        
            # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
        
    # Vocabs
    url(r'^cmip5/vocab/$','cmip5q.protoq.vocab.list',name="vocab_display"),
    (r'^cmip5/vocab/(?P<vocabID>\d+)/$','cmip5q.protoq.vocab.show'),
    #(r'^cmip5/vocab/(?P<docID>\d+)/(?P<valID>\d+)/$','cmip5q.protoq.vocab.list'),
        
    # Atom Feeds
    (r'^feeds/(.*)/$', "django.contrib.syndication.views.feed", {
        "feed_dict": {"cmip5": DocFeed,}
        }
    ),

    # Admin
    (r'', include('cmip5q.protoq.admin.urls')),
    #(r'^admin/protoq/component/copy/$', 'cmip5q.protoq.admin.admin_views.modelcopy'),
    (r'^admin/', include(admin.site.urls)),
    
    # AR5 tables included
    (r'', include('cmip5q.ar5tables.urls')),
    
    # API included
    (r'', include('cmip5q.api.urls')),
)

# now add the common document url methods
#for doc in ['experiment','platform','component','simulation']:
#    for key in ['validate','view','xml','html','export']:
#        urlpatterns+=patterns('',(r'^cmip5/(?P<centre_id>\d+)/%s/(?P<%s_id>\d+)/%s/$'%(doc,doc,key),'cmip5q.protoq.views.doc'))
                        
if True:  # HACK HACK HACK POOR PERFORMANCE AND SECURITY.
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_DOC_ROOT,'show_indexes': True}),
    )
    
# To direct web crawlers to bypass potentially redundant links
urlpatterns += patterns('',
    (r'^robots\.txt$', direct_to_template,
     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)


# finally if necessary, throw it down a level

urlpatterns=patterns('',(r'^%s'%script_path,include(urlpatterns)))