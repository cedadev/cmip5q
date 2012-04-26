from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from cmip5q.explorer.tableHandler import strattable
from cmip5q.explorer.dbvalues import getModels


def home(request):
    '''
    Generates landing page for strat explorer
    '''
    return render_to_response('explorer/strat/home.html', {})


def stratmodeldesc(request):
    '''
    Generates information to complete strat model description table
    '''
    #get real models
    models = getModels()
    #generate information for ar5 table 1
    table1info = strattable(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_strat.home', args=())

    return render_to_response('explorer/strat/modeldesc.html',
                              {'table1': table1info,
                               'urls': urls})
