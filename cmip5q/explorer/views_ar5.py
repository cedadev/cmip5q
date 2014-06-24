import csv
import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from cmip5q.explorer.tableHandler import modeldesctable, ar5table2, ch09table, chemtable
from cmip5q.explorer.model_table import ModelTable
from cmip5q.explorer.dbvalues import getModels, getExps

ar5_modeldesc_fields = [
                        
                        ]


def home(request):
    '''Generates landing page for AR5 explorer
    
    '''
    
    return render_to_response('explorer/ar5/home.html', {})


#------------------------------------------------------------------------------
# View function for creating an ar5 style model description explorer table
#------------------------------------------------------------------------------
def modeldesc(request):
    '''Generates information to complete AR5 table 1, i.e model descriptions
    
    '''
    
    #get models to pass to ModelTable table object 
    models = getModels(pubonly=True)
    
    #retrieve fields to be tabulated 
    fields = ar5_modeldesc_fields
    
    mod_desc = ModelTable(table_title='AR5 Model Description Table', models=models, fields = fields)
    mod_desc = getModels(pubonly=True)
    #generate information for ar5 table 1
    table1info = modeldesctable(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_ar5.home', args=())
    urls['ar5csv'] = reverse('cmip5q.explorer.views_ar5.ar5csv', args=())
    urls['ar5bib'] = reverse('cmip5q.explorer.views_ar5.ar5bib', args=())

    return render_to_response('explorer/ar5/modeldesc.html',
                              {'table1': table1info,
                               'urls': urls})


def create_modeldesc(request):
    '''Generates information to complete AR5 table 1, i.e model descriptions
    
    '''
    
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 table 1
    table1info = modeldesctable(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_ar5.home', args=())
    urls['ar5csv'] = reverse('cmip5q.explorer.views_ar5.ar5csv', args=())
    urls['ar5bib'] = reverse('cmip5q.explorer.views_ar5.ar5bib', args=())

    return render_to_response('explorer/ar5/modeldesc.html',
                              {'table1': table1info,
                               'urls': urls})


def create_ch09table(request):
    '''Generates information from 'new' ch 09 related questions
    
    '''
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 table 1
    ch09tableinfo = ch09table(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_ar5.home', args=())
    urls['ch09csv'] = reverse('cmip5q.explorer.views_ar5.ch09csv', args=())
    urls['ch09bib'] = reverse('cmip5q.explorer.views_ar5.ch09bib', args=())

    return render_to_response('explorer/ar5/ch09table.html',
                              {'ch09table': ch09tableinfo,
                               'urls': urls})


def chem(request):
    '''
    Generates information for the 'chemistry' AR5 table
    '''
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 chem table
    chemtableinfo = chemtable(models)

    # set up my urls ...
    urls = {}
    urls['home'] = reverse('cmip5q.explorer.views_ar5.home', args=())
    urls['chemcsv'] = reverse('cmip5q.explorer.views_ar5.chemcsv', args=())

    return render_to_response('explorer/ar5/chemtable.html',
                              {'chemtable': chemtableinfo,
                               'urls': urls})


def expdesign(request):
    '''
    Generates information to complete AR5 table 2, i.e experiment design
    '''
    #get current experiments
    exps = getExps()
    #generate information for ar5 table 2
    t2reqlist, t2expslist = ar5table2(exps)

    # set up my urls ...
    urls = {}
    urls['ar5home'] = reverse('cmip5q.explorer.views_ar5.home', args=())

    return render_to_response('explorer/ar5/expdesign.html',
                              {'t2explist': t2expslist,
                               't2reqlist': t2reqlist,
                               'urls': urls})


def modelforcing(request):
    '''
    Generates information to complete AR5 table 3, i.e model forcings
    '''
    #----- Table 3 (Forcings) -----
    #temporarily using hadgem2-es model
    #mohc = Centre.objects.get(abbrev='MOHC')
    #hadgem = Component.objects.filter(abbrev="HadGEM2-ES").get(centre=mohc)
    #t3reqlist, t3expslist = ar5table3(exps, hadgem)
    #return HttpResponse('bla bla 3')
    # set up my urls ...

    urls = {}
    urls['ar5home'] = reverse('cmip5q.explorer.views_ar5.home', args=())

    return render_to_response('explorer/ar5/modelforcing.html', {'urls': urls})


def ar5bib(request):
    '''
    Generates a text file of all references used in ar5 table 1
    '''
    #get all models
    models = getModels(pubonly=True)
    table1info = modeldesctable(models)
    #iterate through all models and pull out references
    modelrefs = []
    for model in table1info:
        for refs in [model.maincits, 
                     model.aercits, 
                     model.atmoscits, 
                     model.atmchemcits, 
                     model.licecits, 
                     model.lsurfcits, 
                     model.obgccits, 
                     model.oceancits, 
                     model.seaicecits]:
            if not isinstance(refs, str):
                for ref in refs:
                    if ref[0] == '"' or ref[0] == "'":
                        ref = ref[1:]
                    #check for duplicates before adding
                    if ref + '\n' + '\n' not in modelrefs:
                        modelrefs.append(ref + '\n' + '\n')

    #sort alphabetically and join up into a full string
    modelrefs.sort()
    ar5refs = "".join(modelrefs)

    response = HttpResponse(ar5refs, mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=ar5_refs.txt'

    return response


def ar5csv(request):
    '''
    Generates csv representation of ar5 table 1
    '''
    
    #get date for csv file title
    now = datetime.datetime.now()
    filename = 'ar5csv_modeldesc_%d_%d_%d.csv' % (now.day, now.month, now.year) 
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    #----- Table 1 (Models) -----
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 table 1
    table1info = modeldesctable(models)

    writer = csv.writer(response)

    #write column headings
    writer.writerow(['Model ID| Vintage',

                     'Institution| Main references',
                     
                     'Aerosol component name| Aerosol references',

                     'Atmosphere component name| Atmosphere horizontal grid | Atmosphere grid number of levels| Atmosphere grid top| Atmosphere references',
                     
                     'Atmos chemistry component name| Atmos chemistry references',
                     
                     'land ice component name| Land ice references',
                     
                     'Land surface component name| Land surface references',
                     
                     'Ocean biogeochem component name| Ocean biogeochem references',
                     
                     'Ocean component name| Ocean horizontal grid | Ocean number of levels| Ocean top level| Ocean Z coordinate| Ocean top BC | Ocean references',
                    
                     'Sea ice component name| Sea ice references',
                     
                     ])

    #write out each row of information in turn
    for row in table1info:
        # first group references into a combined string
        maincits = []
        for cit in row.maincits:
            maincits.append(cit + '; ')
        maincits = "".join(maincits).encode("utf-8")

        if not row.aerimplemented:
            aercits = 'None'
        else:
            aercits = []
            for cit in row.aercits:
                aercits.append(cit + '; ')
            aercits = "".join(aercits).encode("utf-8")

        if not row.atmosimplemented:
            atmoscits = 'None'
        else:
            atmoscits = []
            for cit in row.atmoscits:
                atmoscits.append(cit + '; ')
            atmoscits = "".join(atmoscits).encode("utf-8")

        if not row.atmchemimplemented:
            atmchemcits = 'None'
        else:
            atmchemcits = []
            for cit in row.atmchemcits:
                atmchemcits.append(cit + '; ')
            atmchemcits = "".join(atmchemcits).encode("utf-8")

        if not row.liceimplemented:
            licecits = 'None'
        else:                
            licecits=[]
            for cit in row.licecits:
                licecits.append(cit+'; ')
            licecits = "".join(licecits).encode("utf-8")
        
        if not row.lsurfimplemented:
            lsurfcits = 'None'
        else:    
            lsurfcits=[]
            for cit in row.lsurfcits:
                lsurfcits.append(cit+'; ')
            lsurfcits = "".join(lsurfcits).encode("utf-8")
        
        if not row.obgcimplemented:
            obgccits = 'None'
        else:        
            obgccits=[]
            for cit in row.obgccits:
                obgccits.append(cit+'; ')
            obgccits = "".join(obgccits).encode("utf-8")
        
        if not row.oceanimplemented:
            oceancits = 'None'
        else:        
            oceancits=[]
            for cit in row.oceancits:
                oceancits.append(cit+'; ')
            oceancits = "".join(oceancits).encode("utf-8")
                
        if not row.seaiceimplemented:
            seaicecits = 'None'
        else:        
            seaicecits=[]
            for cit in row.seaicecits:
                seaicecits.append(cit+'; ')
            seaicecits = "".join(seaicecits).encode("utf-8")
            
            
        writer.writerow([row.abbrev+'| '+ str(row.yearReleased), 
                         
                         row.centre.name.encode("utf-8")+'| '+ maincits,
                         
                         row.aerabbrev.encode("utf-8")+'| '+aercits,
                         
                         row.atmosabbrev.encode("utf-8")+'| '+row.atmoshorgrid.encode("utf-8")+'| '+row.atmosnumlevels.encode("utf-8")+'| '+row.atmosgridtop.encode("utf-8")+'|'+atmoscits,
                         
                         row.atmchemabbrev.encode("utf-8")+'| '+'| '+atmchemcits,
                        
                         row.liceabbrev.encode("utf-8")+'| '+'| '+licecits,
                         
                         row.lsurfabbrev.encode("utf-8")+'| '+ lsurfcits,
                         
                         row.obgcabbrev.encode("utf-8")+'| '+ obgccits,
                         
                         row.oceanabbrev.encode("utf-8")+'| '+row.oceanhorgrid.encode("utf-8")+'| '+row.oceannumlevels.encode("utf-8")+'| '+row.oceantoplevel.encode("utf-8")+'| '+row.oceanzcoord.encode("utf-8")+'| '+row.oceantopbc.encode("utf-8")+'| '+oceancits,
                         
                         row.seaiceabbrev.encode("utf-8")+'| '+ seaicecits,
                         ])
    
    return response
    
    
def ch09bib(request):
    '''
    Generates a text file of all references used in ar5 table 1
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
    response['Content-Disposition'] = 'attachment; filename=ar5_refs.txt'

    return response


def ch09csv(request):
    '''
    Generates csv representation of ar5 table 1
    '''
    
    #get date for csv file title
    now = datetime.datetime.now()
    filename = 'ar5csv_Tuning_%d_%d_%d.csv' % (now.day, now.month, now.year) 
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    #----- Ch 09 (Models) -----    
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 table 1
    ch09tableinfo = ch09table(models)

    writer = csv.writer(response)

    #write column headings
    writer.writerow(['Model ID',

                     'Institution',
                     
                     'Model Assembly',
                     
                     'Mean State Global Metrics',
                     
                     'Observed Trends Metrics',
                     
                     'Mean State Regional Metrics',
                     
                     'Temporal Variability Metrics',
                     
                     'Adjusted Parameters',
                     
                     'Other Model Tuning?',
                     
                     'Integral Conservation',
                     
                     'Specific Tuning',
                     
                     'Flux Correction Used?',
                     
                     'Flux Correction Fields',
                     
                     'Flux Correction Methods',                     
                     
                     ])

    #write out each row of information in turn
    for row in ch09tableinfo:
        
        # write out list values into strings before entering in csv table
        meanstateglobmets = []
        for met in row.meanstateglobmets:
            meanstateglobmets.append(met+'; ')
        meanstateglobmets = "".join(meanstateglobmets)
        
        obstrendsmets = []
        for met in row.obstrendsmets:
            obstrendsmets.append(met+'; ')
        obstrendsmets = "".join(obstrendsmets)
        
        meanstateregmets = []
        for met in row.meanstateregmets:
            meanstateregmets.append(met+'; ')
        meanstateregmets = "".join(meanstateregmets)
    
        tempvarmets = []
        for met in row.tempvarmets:
            tempvarmets.append(met+'; ')
        tempvarmets = "".join(tempvarmets)
        
        adjparams = []
        for met in row.adjparams:
            adjparams.append(met+'; ')
        adjparams = "".join(adjparams)
        
        intconservation = []
        for met in row.intconservation:
            intconservation.append(met+'; ')
        intconservation = "".join(intconservation)
        
        fluxcorrfields = []
        for met in row.fluxcorrfields:
            fluxcorrfields.append(met+'; ')
        fluxcorrfields = "".join(fluxcorrfields)
        
        
        writer.writerow([row.abbrev, 
                         
                         row.centre.name,
                         
                         row.modelassembly,
                         
                         meanstateglobmets,
                         
                         obstrendsmets,
                         
                         meanstateregmets,
                         
                         tempvarmets,
                         
                         adjparams,
                         
                         row.othmodtuning,
                         
                         intconservation,
                         
                         row.spectuning,
                         
                         row.fluxcorrused,
                         
                         fluxcorrfields,
                         
                         row.fluxcorrmeth,
                         
                         ])
    
    return response
    

def chemcsv(request):
    '''
    Generates csv representation of ar5 chemistry table
    '''
    #get date for csv file title
    now = datetime.datetime.now()
    filename = 'ar5csv_chem_%d_%d_%d.csv' % (now.day, now.month, now.year) 
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    #----- Ch 09 (Models) -----    
    #get real models
    models = getModels(pubonly=True)
    #generate information for ar5 chemistry
    chemtableinfo = chemtable(models)

    writer = csv.writer(response)

    #write column headings
    writer.writerow(['Model ID',

                     'Institution',
                     
                     'Land Surface Carbon Cycle implemented?',
                     
                     'Ocean Bio Chemistry (Carbon Cycle) implemented?',
                     
                     'Aerosol Scheme Type',
                     
                     'Prognostic aerosol treatment',
                     
                     'List of nutrient species',                  
                     
                     ])

    #write out each row of information in turn
    for row in chemtableinfo:        
        
        writer.writerow([row.abbrev, 
                         
                         row.centre.name,
                         
                         row.lsccimplemented,
                         
                         row.occimplemented,
                         
                         row.aerscheme,
                         
                         row.aermoments,
                         
                         row.ocbiotracnuts,
                         
                         ])
    
    return response
     
