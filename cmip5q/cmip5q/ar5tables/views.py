import csv

from django.shortcuts import render_to_response
from django.http import HttpResponse

from cmip5q.ar5tables.tableHandler import ar5table1, ar5table2
from cmip5q.ar5tables.utilities import getModels, getExps


def ar5tables(request): 
    '''
    Generate information to complete AR5 tables 
    '''   
    
    #----- Table 1 (Models) -----
    #get real models
    models = getModels()
    #generate information for ar5 table 1    
    table1info = ar5table1(models)
    
    #----- Table 2 (Experiments) -----
    #get current experiments
    exps = getExps()
    #generate information for ar5 table 2
    table2info = ar5table2(exps)
    
    #----- Table 3 (Forcings) -----
    #TO DO
        
    return render_to_response('ar5/ar5tables.html',{'table1':table1info, 
                                                'table2':table2info})
    

def ar5csv(request):
    '''
    Generate csv representation of ar5 table 1
    '''
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=ar5csv_table1.csv'
    
    #----- Table 1 (Models) -----
    #get real models
    models = getModels()
    #generate information for ar5 table 1    
    table1info = ar5table1(models)
    
    writer = csv.writer(response)
    
    #write column headings
    writer.writerow(['Model ID', 
                     'Vintage', 
                     'Institution', 
                     'Atmosphere,Top', 
                     'Hor. Resolution',
                     'Atmos Refs',
                     'Ocean Resolution',
                     'Ocean Z Coordinate',
                     'Ocean Top BC',
                     'Ocean Refs',
                     'Sea Ice Rheology',
                     'Water Ponds?',
                     'Lateral Melting?',
                     'Sea Ice Refs',
                     'River Routing?',
                     'Land Surface Refs',
                     ])
    
    #write out each row of information in turn
    for row in table1info: 
        # first group references into a combined string
        atmoscits=[]
        for cit in row.atmoscits:
            atmoscits.append(cit+'; ')
        oceancits=[]
        for cit in row.oceancits:
            oceancits.append(cit+'; ')
        seaicecits=[]
        for cit in row.seaicecits:
            seaicecits.append(cit+'; ')
        lscits=[]
        for cit in row.lscits:
            lscits.append(cit+'; ')
            
        writer.writerow([row.abbrev, 
                         row.yearReleased, 
                         row.centre.name, 
                         row.atmosgridtop, 
                         row.atmoshorgrid,
                         "".join(atmoscits),
                         row.oceangrid,
                         row.zcoord,
                         row.topbc,
                         "".join(oceancits),
                         row.sirheol,
                         row.siwaterpond,
                         row.silatmelt,
                         "".join(seaicecits),
                         row.riverrouting,
                         "".join(lscits),
                         ])
    
    return response
    
    
     
