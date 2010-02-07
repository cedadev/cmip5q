from protoq.models import *
import csv
from django.conf import settings
logging=settings.LOG


def initialiseRefs():
    ''' This routine initialises the database with some obvious files for boundary conditoins etc '''
    CSVinfo = csv.reader(open('data/References/Refs_CSV.csv'), delimiter=';', quotechar='|')
    # this is the vocab that we always use for reference types:
    v=Vocab.objects.get(name='ReferenceTypes')
    # loop over all rerences in spreadsheet
    for row in CSVinfo:
        print row
        logging.debug(', '.join(row))
        name,citation,link=tuple(row)
        # find out what refrence type
        myreftype='Online Refereed'
        try:
            refType=Value.objects.filter(vocab=v).get(value=myreftype)
        except:
            logging.info('Ignoring reference %s'%', '.join(row))
            break  # leave the loop
        # find the other things: name, citation, link    
        r=Reference(name=name,
                    citation=citation,
                    link=link,
                    refTypes=v,
                    refType=refType)
        try:
            r.save()
        except:
            logging.info('Unable to save reference %s'%name)
        # temporary 2 lines
        def __unicode__(self):
            return
    
if __name__=="__main__":
    
     initialiseRefs()