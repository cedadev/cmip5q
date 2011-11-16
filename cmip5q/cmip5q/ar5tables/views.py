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
    writer.writerow(['Model ID| Vintage',
                     
                     'Institution| Main references| Flux correction',
                     
                     'Aerosol component name| Aerosol code independance| Aerosol references',
                     
                     'Atmosphere component name| Atmosphere horizontal grid | Atmosphere grid number of levels| Atmosphere grid top| Atmosphere code independance | Atmosphere references',
                     
                     'Atmos chemistry component name| Atmos chemistry code independance | Atmos chemistry references',
                     
                     'land ice component name| Land ice code independance| Land ice references',
                     
                     'Land surface component name| Land surface code independance | Land surface references',
                     
                     'Ocean biogeochem component name| Ocean biogeochem code independance | Ocean biogeochem references',
                     
                     'Ocean component name| Ocean horizontal grid | Ocean number of levels| Ocean top level| Ocean Z coordinate| Ocean top BC | Ocean code independance | Ocean references',
                     
                     'Sea ice component name| Sea ice code independance| Sea ice references',
                     
                     ])
    
    #write out each row of information in turn
    for row in table1info: 
        # first group references into a combined string
        maincits=[]
        for cit in row.maincits:
            maincits.append(cit+'; ')
        maincits = "".join(maincits)
        
        if not row.aerimplemented:
            aercits = 'None'
        else:
            aercits=[]
            for cit in row.aercits:
                aercits.append(cit+'; ')
            aercits = "".join(aercits)
        
        if not row.atmosimplemented:
            atmoscits = 'None'
        else:
            atmoscits=[]
            for cit in row.atmoscits:
                atmoscits.append(cit+'; ')
            atmoscits = "".join(atmoscits)
        
        if not row.atmchemimplemented:
            atmchemcits = 'None'
        else:        
            atmchemcits=[]
            for cit in row.atmchemcits:
                atmchemcits.append(cit+'; ')
            atmchemcits = "".join(atmchemcits)
        
        if not row.liceimplemented:
            licecits = 'None'
        else:                
            licecits=[]
            for cit in row.licecits:
                licecits.append(cit+'; ')
            licecits = "".join(licecits)
        
        if not row.lsurfimplemented:
            lsurfcits = 'None'
        else:    
            lsurfcits=[]
            for cit in row.lsurfcits:
                lsurfcits.append(cit+'; ')
            lsurfcits = "".join(lsurfcits)
        
        if not row.obgcimplemented:
            obgccits = 'None'
        else:        
            obgccits=[]
            for cit in row.obgccits:
                obgccits.append(cit+'; ')
            obgccits = "".join(obgccits)
        
        if not row.oceanimplemented:
            oceancits = 'None'
        else:        
            oceancits=[]
            for cit in row.oceancits:
                oceancits.append(cit+'; ')
            oceancits = "".join(oceancits)
                
        if not row.seaiceimplemented:
            seaicecits = 'None'
        else:        
            seaicecits=[]
            for cit in row.seaicecits:
                seaicecits.append(cit+'; ')
            seaicecits = "".join(seaicecits)
            
            
        writer.writerow([row.abbrev+'| '+str(row.yearReleased), 
                         
                         row.centre.name+'| '+"".join(maincits)+'| '+'Flux correction field',
                         
                         row.aerabbrev+'| '+'XX%'+'| '+aercits,
                         
                         row.atmosabbrev+'| '+row.atmoshorgrid+'| '+row.atmosnumlevels+'| '+row.atmosgridtop+'| '+'XX%'+'| '+"".join(atmoscits),
                         
                         row.atmchemabbrev+'| '+'XX%'+'| '+"".join(atmchemcits),
                         
                         row.liceabbrev+'| '+'XX%'+'| '+"".join(licecits),
                         
                         row.lsurfabbrev+'| '+'XX%'+'| '+"".join(lsurfcits),
                         
                         row.obgcabbrev+'| '+'XX%'+'| '+"".join(obgccits),
                         
                         row.oceanabbrev+'| '+row.oceanhorgrid+'| '+row.oceannumlevels+'| '+row.oceantoplevel+'| '+row.oceanzcoord+'| '+row.oceantopbc+'| '+'XX%'+'| '+"".join(oceancits),
                         
                         row.seaiceabbrev+'| '+'XX%'+'| '+"".join(seaicecits),
                         ])
    
    return response
    
    
     
