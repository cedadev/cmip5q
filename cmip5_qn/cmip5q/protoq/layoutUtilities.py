
import string

from django.conf import settings
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.utilities import RingBuffer

logging=settings.LOG


def esgurl(modelname=None, simname=None):
    '''
    Return a url construct for cim document viewing within the ESG portal
    ''' 
    
    esgurl = 'http://www.earthsystemgrid.org/trackback/query.htm?id=esg%3amodel_' \
      +modelname+'_'+simname+'&session=true'
    
    return esgurl
  
  
def cimviewer(drs):
    ''' 
    '''
    splitter = str(drs).split('_')
    idString = 'cmip5/' + splitter[0].lower().replace(' ', '-')  + '/' + splitter[1].lower() + '/' + splitter[2] + '/' + splitter[3] + '/' + splitter[4]
    
    return idString
    


def getpubs():
    '''
    Return a list of published CIM documents for instantiating a datatable 
    '''
    
    # Create a dictionary of document type mapping terms 
    cimTypes={'simulation':{'class':Simulation},
              'component':{'class':Component},
              'experiment':{'class':Experiment},
              'grid':{'class':Grid},
              'platform':{'class':Platform},
             }
    
    # generate initial queryset of all CIMObjects (not including exps for now)
    allpubs = list(CIMObject.objects.exclude(cimtype='experiment').order_by('created'))
    # only take the latest version of each document
    pubs=[]
    for pub in allpubs:
        # Check if I'm a duplicate
        duplicates = list(CIMObject.objects.filter(uri=pub.uri).order_by('documentVersion'))
        if len(duplicates)>1:
            # If so, include me if I'm the most recent
            if pub == duplicates[-1]:
                pubs.append(pub)
        else:
            pubs.append(pub)
    
    for pub in pubs:
        
        # attach extra attributes to queryset
        cimType=pub.cimtype
        
        if cimType not in cimTypes:
            raise ValueError('Unknown cim type %s' %cimType)
        try:
            cimTarget = cimTypes[cimType]
            document = cimTarget['class'].objects.filter(isDeleted=False).get(
                                                                    uri=pub.uri)
            
            # attach document centre name
            #replace any spaces with - to bring in line with drs
            pub.centrename = str(document.centre).replace(' ', '-')
            pub.abbreviation = document.abbrev
            
            # attach a url path to esg portal view (limited to most recent 
            # version of simulations) - also get the models/exps used for 
            # simulations
            # - also get the cimviewID qndrs id for the link out to the CIM viewer plugin 
            try: 
                if cimType =='simulation':
                    #get most up-to-date version
                    utdsim = (CIMObject.objects.filter(uri=pub.uri).order_by(
                                                        '-documentVersion'))[0]
                    if pub == utdsim:
                        modelname = str(document.numericalModel).lower()
                        expname = str(document.experiment).lower()
                        simname = str(document.abbrev) \
                              .replace(" ","_").lower()
                        
                        #attach esg url link
                        pub.esgurl = esgurl(modelname=modelname, 
                                            simname=simname)
                        #attach qndrs for cim viewer
                        pub.cimviewID = cimviewer(document.drsOutput.all()[0])
                        #attach model name associated with simulation
                        pub.usesmodel = modelname
                        pub.forexp = expname
                    else:
                        pub.esgurl = ''
                        pub.cimviewID= ''
                        pub.usesmodel = '---'
                        pub.forexp = '---'
                else:
                    pub.usesmodel = '---'                    
                    pub.forexp = '---'
            except:
                pub.esgurl = ''
                pub.cimviewID = ''
                pub.usesmodel = '---'
                pub.forexp = '---'
                
        except:
            pub.centrename = ''
            pub.esgurl = ''
            pub.cimviewID = ''
            
    return pubs


def getdoidocs(institute, modelname, expname):
    '''
    Return a list of published simulation CIM documents for a doi landing page  
    '''
        
    # generate initial queryset of all simulation CIMObjects
    allsimpubs = list(CIMObject.objects.filter(cimtype='simulation').order_by('created'))
    # only take the latest version of each document
    simpubs = []
    for simpub in allsimpubs:
        # Check if I'm a duplicate
        duplicates = list(CIMObject.objects.filter(uri=simpub.uri).order_by('documentVersion'))
        if len(duplicates)>1:
            # If so, include my simulation instance if I'm the most recent
            if simpub == duplicates[-1]:
                mysim = Simulation.objects.filter(isDeleted=False).get(uri=simpub.uri)
                simpubs.append(mysim)
        else:
            # I'm the only version so add me
            mysim = Simulation.objects.filter(isDeleted=False).get(uri=simpub.uri)
            simpubs.append(mysim)
            
    # now filter me by given institute, model, and experiment to make a list for the doi page
    simdoipubs = []
    for sim in simpubs:
        # In the case of 'decadal' and 'noVolc' experiments we need to append the start year
        if str(sim.experiment).split(' ')[1] in ["decadal", "noVolc"]:
            # need to finally check  if start date is january 1st in which case
            # this will apply to a simulation for the year before (see cmip5 
            # experiment design document)
            if str(sim.duration.startDate.mon) == '1' and str(sim.duration.startDate.day) == '1':
                expupdated = str(sim.experiment).split(' ')[1] + str(sim.duration.startDate.year - 1)
            else:
                expupdated = str(sim.experiment).split(' ')[1] + str(sim.duration.startDate.year)
              
        else:
            expupdated = str(sim.experiment).split(' ')[1]
        
        if str(sim.centre).replace(' ', '-').lower() == institute.lower() and str(sim.numericalModel).replace(' ', '-').lower() == modelname.lower() and expupdated.lower() == expname.lower():
          # add me as I fit the query parameters
          sim.cimviewID = cimviewer(sim.drsOutput.all()[0])
          sim.exp = str(sim.experiment).split(' ')[1]
          sim.member = str(sim.drsOutput.all()[0].member).split(' ')[0]
          sim.startyear = sim.drsOutput.all()[0].startyear
          simdoipubs.append(sim)
    
    # Check that at least one document has been found for the given query parameters:
    if len(simdoipubs) == 0:
        #return a message stating no docs found
        pass
        
    
    return simdoipubs
  

def getsims(centre):
    '''
    Return a list of centre simulations for instantiating a datatable 
    '''
       
    # generate initial queryset of all simulations
    tablesims = Simulation.objects.filter(centre=centre).filter(isDeleted=False)
    
    for s in tablesims:
        #get individual sim edit url
        s.url=reverse('cmip5q.protoq.views.simulationEdit', 
                      args=(centre.id,s.id))   
        #get individual sim copy url
        s.copysimurl=reverse('cmip5q.protoq.views.simulationCopyInd', 
                         args=(centre.id,s.id))
        #get individual sim delete url (for non-published sims)
        if len(CIMObject.objects.filter(uri=s.uri)):
            s.delurl = None
        else:     
            s.delurl=reverse('cmip5q.protoq.views.simulationDel', 
                         args=(centre.id,s.id))     
    
    return tablesims


class tab:
    ''' 
    This is a simple tab class to support navigation tabs 
    '''
    
    def __init__(self,name,url,active=0, pos='left'):
        self.name=name # what is seen in the tab
        self.url=url
        self.active=active
        self.pos=pos
        #print 't[%s,%s]'%(self.name,self.url)
    def activate(self):
        self.active=1
    def deactivate(self):
        self.active=0
    def obscure(self):
        self.active=-1


class tabs(list):
    ''' 
    Build a list of tabs to be used on each page, and provide a history 
    list, via cookie, to be passed to base.html 
    '''
    
    history_length=5
    
    def __init__(self,request,centre_id,page,object_id=0):
        list.__init__(self)
        self.request=request
        self.centre=Centre.objects.get(id=centre_id)
        # we keep the last model and simulation in the session cookie
        if page=='Model':
            request.session['Model']=object_id
        elif page=='Simulation':
            request.session['Simulation']=object_id
        elif page=='Grid':
            request.session['Grid']=object_id
            
        # need to allow for the case when neither have yet been viewed
        if 'Simulation' not in request.session:request.session['Simulation']=0
        if 'Model' not in request.session:request.session['Model']=0
        if 'Grid' not in request.session:request.session['Grid']=0
        
        #This is the list of tabs '''
        self.tablist=[
            ('Summary', 'cmip5q.protoq.views.centre', (centre_id,), 'left'),
            ('Experiments', 'cmip5q.protoq.views.simulationList', 
                 (centre_id,), 'left'),
            ('Model', 'cmip5q.protoq.views.componentEdit', 
                 (centre_id, request.session['Model'],), 'left'),
            ('Grid', 'cmip5q.protoq.views.gridEdit', 
                 (centre_id, request.session['Grid'],) ,'left'),
            ('Simulation', 'cmip5q.protoq.views.simulationEdit', 
                 (centre_id, request.session['Simulation'],), 'left'),
            ('Files', 'cmip5q.protoq.views.list', 
                 (centre_id, 'file',), 'left'),
            ('References', 'cmip5q.protoq.views.list', 
                 (centre_id, 'reference',), 'left'),
            ('Parties', 'cmip5q.protoq.views.list', 
                 (centre_id, 'parties',), 'left'),
            ('Help', 'cmip5q.protoq.views.help', 
                 (centre_id,), 'right'),
            ('About', 'cmip5q.protoq.views.about', 
                 (centre_id,), 'right'),
            ('Log Out', 'right'),
            ]
        
        for item in self.tablist:
            self.append(self.tabify(item,page))
            
        self.history(request,page)
            
    def tabify(self,item,page):
        if item[0] not in ['Simulation','Model','Grid']:
            #it's easy:
            if item[0] not in ['Log Out']:
                return tab(item[0], reverse(item[1], args=item[2]), 
                           page==item[0], item[3])
            else:
                return tab(item[0], 
                    #'http://q.cmip5.ceda.ac.uk/logout?ndg.security.r=http%3A//q.cmip5.ceda.ac.uk/', 
                     'http://q.cmip5.ceda.ac.uk/logout',
                    page==item[0], item[1])
        else:
            if item[2][1]==0:
                return tab(item[0],'',-1, item[3])
            else: 
                try:
                    obj={'Model':Component,'Simulation':Simulation,'Grid':Grid}[item[0]].objects.get(id=item[2][1])
                except:
                    logging.info('Attempt to access deleted component, simulation or grid %s,%s'%(item[0],item[2][1]))
                    return tab(item[0],'',-1,item[3] )
                return tab('%s:%s'%(item[0][0:5],obj),
                           reverse(item[1],args=item[2]),
                           page==item[0], item[3])
            
            
    def history(self,request,page):
        #initialise as necessary.
        if 'History' not in request.session:request.session['History']=RingBuffer(self.history_length)
        #append the path and name for later use in a link ...
        request.session['History'].append((request.path,page))
     
