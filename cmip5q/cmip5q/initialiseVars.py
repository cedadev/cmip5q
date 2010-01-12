from protoq.models import *
import csv
import logging

def initialiseVars():
    ''' This routine initialises the database with variables contained within 'standard' files for boundary conditions etc '''
    VarsCSVinfo = csv.reader(open('data/References/Vars_CSV.csv'), delimiter=';', quotechar='|')
    
    # loop over all variables in spreadsheet
    for row in VarsCSVinfo:
        parentfile,description,variable=tuple(row)
        logging.debug(parentfile+variable)
        try:
            container=DataContainer.objects.get(name=parentfile)
        except:
            logging.info('Ignoring variable %s'%variable)
            break  # leave the loop  
        f=DataObject(container=container,
                    description=description,
                    variable=variable)
        try:
            r=f.save()
        except:
            logging.info('Unable to save variable %s (%s)'%(variable,r))
    
if __name__=="__main__":
    
    initialiseVars()    