
from django.conf import settings
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from cmip5q.protoq.models import *
from cmip5q.protoq.utilities import RingBuffer

logging=settings.LOG

class tab:
    ''' This is a simple tab class to support navigation tabs '''
    def __init__(self,name,url,active=0):
        self.name=name # what is seen in the tab
        self.url=url
        self.active=active
        #print 't[%s,%s]'%(self.name,self.url)
    def activate(self):
        self.active=1
    def deactivate(self):
        self.active=0
    def obscure(self):
        self.active=-1

class tabs(list):
    ''' Build a list of tabs to be used on each page, and provide a history list, 
        via cookie, to be passed to base.html '''
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
        # need to allow for the case when neither have yet been viewed
        if 'Simulation' not in request.session:request.session['Simulation']=0
        if 'Model' not in request.session:request.session['Model']=0
        #This is the list of tabs '''
        self.tablist=[#('Intro','cmip5q.protoq.views.intro',(centre_id,)),
                 ('Summary','cmip5q.protoq.views.centre',(centre_id,)),
                 ('Experiments','cmip5q.protoq.views.simulationList',(centre_id,)),
                 ('Model','cmip5q.protoq.views.componentEdit',(centre_id,request.session['Model'],)),
                 ('Grids','cmip5q.protoq.views.list',(centre_id,'grid',)),
                 ('Simulation','cmip5q.protoq.views.simulationEdit',(centre_id,request.session['Simulation'],)),
                 ('Files','cmip5q.protoq.views.list',(centre_id,'file',)),
                 ('References','cmip5q.protoq.views.list',(centre_id,'reference',)),
                 ('Parties','cmip5q.protoq.views.list',(centre_id,'parties',)),
                 ('Help','cmip5q.protoq.views.help',(centre_id,)),
                 ('About','cmip5q.protoq.views.about',(centre_id,)),
                 ]
        for item in self.tablist:
            self.append(self.tabify(item,page))
            
        self.history(request,page)
            
    def tabify(self,item,page):
        if item[0] not in ['Simulation','Model']:
            #it's easy:
            return tab(item[0],reverse(item[1],args=item[2]),page==item[0])
        else:
            if item[2][1]==0:
                return tab(item[0],'',-1)
            else: 
                try:
                    obj={'Model':Component,'Simulation':Simulation}[item[0]].objects.get(id=item[2][1])
                except:
                    logging.info('Attempt to access deleted component or simulation %s,%s'%(item[0],item[2][1]))
                    return tab(item[0],'',-1)
                return tab('%s:%s'%(item[0][0:3],obj),
                           reverse(item[1],args=item[2]),
                           page==item[0])
            
    def history(self,request,page):
        #initialise as necessary.
        if 'History' not in request.session:request.session['History']=RingBuffer(self.history_length)
        #append the path and name for later use in a link ...
        request.session['History'].append((request.path,page))
     
