from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    #
    # Questionnaire API for xml dump of number of qn docs:
    #
    (r'^numdocs$','cmip5q.qnstats.views.numdocs'),
    
    #
    # text based view of qn stats
    #
    (r'^$','cmip5q.qnstats.views.stats_summary'),
    
                
    )

