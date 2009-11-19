import logging
from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse

def RemoteUser(request,document):
    ''' Assign a metadata maintainer if we have one '''
    key='REMOTE_USER'
    #if key in request.META:
        #user=request.META[key]
        #document.metadataMaintainer=ResponsibleParty( ...)
        #document.save()
    return document

class RingBuffer:
    def __init__(self, size):
        self.data = [None for i in xrange(size)]
    def append(self, x):
        self.data.pop(0)
        self.data.append(x)
    def get(self):
        return self.data

def sublist(alist,n):
    ''' Take a list, and return a list of lists, where each of the sublists has n members
    except possibly the last '''
    nn=len(alist)
    nsubs=nn/n
    fragment=0
    if nsubs*n<nn:fragment=1
    blist=[]
    for i in range(nsubs):
        blist.append(alist[i*n:(i+1)*n])
    if fragment:
        blist.append(alist[nsubs*n:])
    return blist

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
                obj={'Model':Component,'Simulation':Simulation}[item[0]].objects.get(id=item[2][1])
                return tab('%s:%s'%(item[0][0:3],obj),
                           reverse(item[1],args=item[2]),
                           page==item[0])
            
    def history(self,request,page):
        #initialise as necessary.
        if 'History' not in request.session:request.session['History']=RingBuffer(self.history_length)
        #append the path and name for later use in a link ...
        request.session['History'].append((request.path,page))
     
class NewPropertyForm:
    
    def __init__(self,component,prefix=''):
        
        self.prefix=prefix
        self.component=component
        
        # filter chaining, see
        # http://docs.djangoproject.com/en/dev/topics/db/queries/#chaining-filters
        pgset=self.component.paramgroup_set.all()
        self.keys={}
        self.pgset=[]
        for pg in pgset:
            pg.cgset=[]            
            for cg in pg.constraintgroup_set.all():
                params=cg.newparam_set.all()
                cg.orp=params.filter(ptype='OR')
                cg.xorp=params.filter(ptype='XOR')
                cg.other=params.exclude(ptype='XOR').exclude(ptype='OR')
                cg.controlled=params.exclude(ptype='User')
                cg.rows=[]
                for o in cg.orp:
                    o.form={'op':'+='}
                    o.form['values']=[str(i) for i in Value.objects.filter(vocab=o.vocab)]
                    o.form['values'].insert(0,'------')
                    o.key=o.id
                    cg.rows.append(o)
                for o in cg.xorp:
                    o.form={'op':'='}
                    o.form['values']=[str(i) for i in Value.objects.filter(vocab=o.vocab)]
                    o.form['values'].insert(0,'------')
                    o.key=o.id
                    cg.rows.append(o)
                for o in cg.other:
                    o.form=None
                    o.key=o.id
                    cg.rows.append(o)
                pg.cgset.append(cg)
            self.pgset.append(pg)
            
    def update(self,request):
        ''' take an incoming form and load it into the database '''
        qdict=request.POST
        
        lenprefix=len(self.prefix)
        deleted=[]
        
        for key in qdict.keys():
            # only handle those which belong here:
            if key[0:lenprefix]==self.prefix:
                mykey=key[lenprefix+1:]
                myids=mykey.split('/') 
                # four cases, new params and values, deletions, and controlled values
                if 'newparamval' in mykey:
                    #ignore, handled below
                    pass
                elif 'newparam' in mykey:
                    id=mykey[0:mykey.find('newparam')-1]
                    name=qdict[key]
                    if qdict[key]<>'':
                        nvalkey='%s-%s-newparamval'%(self.prefix,id)
                        if nvalkey not in qdict:
                            logging.info('New param value expected, nothing added(%s)'%qdict)
                        else:
                            try:
                                cg=ConstraintGroup.objects.get(id=id)
                                new=NewParam(name=name,value=qdict[nvalkey],ptype='User',constraint=cg)
                                new.save()
                            except:
                                logging.info('Unable to load new parameter %s into %s'%(name,id))
                elif mykey[0:3] == 'del':
                    # we can only delete user defined things ...
                    id=mykey[4:]
                    try:
                        p=NewParam.objects.get(id=id)
                        p.delete()
                        deleted.append(id)
                        logging.info('Deleted parameter %s from %s'%(id,self.component))
                    except:
                        logging.info(
                          'Attempt to delete parameter %s for component %s failed '%(id,self.component))
                else:
                    if mykey not in deleted:
                        try:
                            p=NewParam.objects.get(id=mykey)
                            p.value=qdict[key]
                            p.save()
                        except:
                            logging.info('Unable to load (new)parameter value for %s (val %s)'%(mykey,qdict[key]))