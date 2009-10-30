from protoq.models import *
import csv
import logging

def initialiseFiles():
    ''' This routine initialises the database with some obvious files for boundary conditoins etc '''
    FilesCSVinfo = csv.reader(open('Files_CSV.csv'), delimiter=';', quotechar='|')
    # this is the vocab that we always use for reference types:
    v=Vocab.objects.get(name='FileFormats')
    # loop over all rerences in spreadsheet
    for row in FilesCSVinfo:
        print row
        logging.debug(', '.join(row))
        # format is being read into the tuple only for convenience at the moment but is overwritten
        name,link,format,description=tuple(row)
        # find out what file type
        filetype='Other'
        try:
            format=Value.objects.filter(vocab=v).get(value=filetype)
        except:
            logging.info('Ignoring file %s'%', '.join(row))
            break  # leave the loop
        # find the other things: name, description, link    
        f=DataContainer(name=name,
                    link=link,
                    description=description,
                    format=format)
        try:
            f.save()
        except:
            logging.info('Unable to save file %s'%name)
        # temporary 2 lines
        def __unicode__(self):
            return
    
if __name__=="__main__":
    
    initialiseFiles()    