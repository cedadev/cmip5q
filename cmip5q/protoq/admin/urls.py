from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/protoq/component/copy/$', 'cmip5q.protoq.admin.admin_views.modelcopy'),
)
