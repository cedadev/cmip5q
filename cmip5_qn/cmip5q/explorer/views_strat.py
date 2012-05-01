import csv

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


def modeldesc(request):
    '''
    Generates information to complete strat model description table
    '''
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 table 1
    table1info = strattable(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_strat.home', args=())
    urls['stratcsv'] = reverse('cmip5q.explorer.views_strat.stratcsv', args=())
    urls['stratbib'] = reverse('cmip5q.explorer.views_strat.stratbib', args=())

    return render_to_response('explorer/strat/modeldesc.html',
                              {'table1': table1info,
                               'urls': urls})


def stratbib(request):
    '''
    Generates a text file of all references used in strat table
    '''
    #get all models
    models = getModels()
    #iterate through all models and pull out references
    modelrefs = []
    for model in models:
        refs = model.references.all()
        for ref in refs:
            #check for duplicates before adding
            if ref.citation + '\n' + '\n' not in modelrefs:
                modelrefs.append(ref.citation + '\n' + '\n')

    #sort alphabetically and join up into a full string
    modelrefs.sort()
    ar5refs = "".join(modelrefs)

    response = HttpResponse(ar5refs, mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=strat_refs.txt'

    return response


def stratcsv(request):
    '''
    Generates csv representation of strat table
    '''
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=stratcsv_table1.csv'

    #----- Table 1 (Models) -----
    #get real models
    models = getModels()
    #generate information for ar5 table 1
    tableinfo = strattable(models)

    writer = csv.writer(response)

    #write column headings
    writer.writerow(['Model ID| Vintage',

                     'Institution| Main references',

                     'Atmosphere component name| Atmosphere horizontal grid | Atmosphere grid number of levels| Atmosphere grid top| Atmosphere references',

                     'Source mechanisms| Propogation scheme | Dissipation scheme',

                     'Strat. het. chem. gas species| Strat. het. chem. aerosol',

                     ])

    #write out each row of information in turn
    for row in tableinfo:
        # first group references into a combined string
        maincits = []
        for cit in row.maincits:
            maincits.append(cit + '; ')
        maincits = "".join(maincits)

        if not row.atmosimplemented:
            oroggwsrcs = 'None'
        else:
            srcs = []
            for src in row.oroggwsrcs:
                srcs.append(src + '; ')
            oroggwsrcs = "".join(srcs)

        if not row.atmosimplemented:
            atmoscits = 'None'
        else:
            atmoscits = []
            for cit in row.atmoscits:
                atmoscits.append(cit + '; ')
            atmoscits = "".join(atmoscits)

        if not row.atmchemimplemented:
            strathetchemgas = 'None'
        else:
            srcs = []
            for src in row.strathetchemgas:
                srcs.append(src + '; ')
            strathetchemgas = "".join(srcs)

        if not row.atmchemimplemented:
            strathetchemaer = 'None'
        else:
            srcs = []
            for src in row.strathetchemaer:
                srcs.append(src + '; ')
            strathetchemaer = "".join(srcs)

        writer.writerow([row.abbrev + '| ' + str(row.yearReleased),

                         row.centre.name + '| ' + "".join(maincits),

                         row.atmosabbrev+'| ' + row.atmoshorgrid+'| ' + row.atmosnumlevels + '| ' + row.atmosgridtop + '| '+"".join(atmoscits),

                         oroggwsrcs+'| '+row.oroggwprop +'| '+row.oroggwdiss,

                         strathetchemgas + '| ' + strathetchemaer

                         ])

    return response
