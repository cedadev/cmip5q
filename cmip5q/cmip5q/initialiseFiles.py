from protoq.models import *
import csv
import logging

def initialiseFiles():
    ''' This routine initialises the database with some obvious files for boundary conditoins etc '''
    FilesCSVinfo = csv.reader(open('data/References/Files_CSV.csv'), delimiter=';', quotechar='|')
    # this is the vocab that we always use for reference types:
    v=Vocab.objects.get(name='FileFormats')
    # loop over all references in spreadsheet
    for row in FilesCSVinfo:
        # format is being read into the tuple only for convenience at the moment but is overwritten
        name,link,filetype,description=tuple(row)
        logging.debug(name+filetype)
        # find out what file type
        #filetype='Other'
        try:
            format=Value.objects.filter(vocab=v).get(value=filetype)
        except:
            logging.info('Ignoring file %s'%name)
            break  # leave the loop
        # find the other things: name, description, link    
        f=DataContainer(name=name,
                    link=link,
                    description=description,
                    format=format)
        try:
            r=f.save()
        except:
            logging.info('Unable to save file %s (%s)'%(name,r))
    
if __name__=="__main__":
    
    initialiseFiles()    