import logging
from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse

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
        
        self.pg=ParamGroup.objects.filter(component=component)
        
        self.keys={}
        
        for pg in self.pg:
            pg.constraintGroup=ConstraintGroup.objects.filter(parentGroup=pg)
            for cg in pg.constraintGroup:
                
                params=NewParam.objects.filter(constraint=cg)
                cg.orp=params.filter(ptype='OR')
                cg.xorp=params.filter(ptype='XOR')
                cg.other=params.exclude(ptype='XOR').exclude(ptype='OR')
                cg.controlled=params.exclude(ptype='User')
             
                cg.rows=[]
                cg.keys=[]
        
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
                if mykey == 'newparam':
                    if qdict[key]<>'':
                        nvalkey='%s-newparamval'%self.prefix
                        if nvalkey not in qdict:
                            logging.info('New param value expected, nothing added(%s)'%qdict)
                        else:
                            #  assumption is that the user constraint and parameter group is the last one.
                            new=Param(name=qdict[key],value=qdict[nvalkey],ptype='User',
                                constraint=self.pg[-1].cg[-1])
                            new.save()
                elif mykey == 'newparamval':
                    #ignore, handled above
                    pass
                elif mykey[0:3] == 'del':
                    # we can only delete user defined things ...
                    pname=mykey[4:]
                    try:
                        p=Param.objects.get(id=pname)
                        p.delete()
                        deleted.append(pname)
                        logging.info('Deleted parameter %s from %s'%(pname,self.component))
                    except:
                        logging.info(
                          'Attempt to delete parameter %s for component %s failed '%(
                              pname,self.component))
                else:
                    if mykey not in self.keys:
                        logging.info(
                        'Unexpected key %s ignored in PropertyForm (%s)'%(
                        mykey,self.keys))
                    else:
                        if mykey not in deleted:
                            p=self.params.get(id=mykey)
                            new.value=qdict[key]
                            new.save()

     
        
class PropertyForm:
    
    ''' this class instantiates the form elements needed by a component view
    of questionnaire properties aka parameters '''
    
    def __init__(self,component,prefix=''):
        
        self.prefix=prefix
        self.component=component
        
        # filter chaining, see
        # http://docs.djangoproject.com/en/dev/topics/db/queries/#chaining-filters
        self.params=Param.objects.filter(component=component)
        self.orp=self.params.filter(ptype='OR')
        self.xorp=self.params.filter(ptype='XOR')
        self.other=self.params.exclude(ptype='OR').exclude(ptype='XOR')
        self.controlled=self.params.exclude(ptype='User')
        
        self.rows=[]
        self.keys={}
        
        for o in self.orp:
            o.form={'op':'+='}
            o.form['values']=[str(i) for i in Value.objects.filter(vocab=o.vocab)]
            o.form['values'].insert(0,'------')
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
        
        for o in self.xorp:
            o.form={'op':'='}
            o.form['values']=[str(i) for i in Value.objects.filter(vocab=o.vocab)]
            o.form['values'].insert(0,'------')
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
            
        for o in self.other:
            o.form=None
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
            
                        
    def update(self,request):
        ''' Update a parameter field based on a form posted inwards '''
        qdict=request.POST
        lenprefix=len(self.prefix)
        deleted=[]
        for key in qdict.keys():
            # only handle those which belong here:
            if key[0:lenprefix]==self.prefix: 
                mykey=key[lenprefix+1:]
                if mykey == 'newparam':
                    if qdict[key]<>'':
                        nvalkey='%s-newparamval'%self.prefix
                        if nvalkey not in qdict:
                            logging.info('New param value expected, nothing added(%s)'%qdict)
                        else:
                            new=Param(name=qdict[key],value=qdict[nvalkey],ptype='User',
                                component=self.component)
                            new.save()
                elif mykey == 'newparamval':
                    #ignore, handled above
                    pass
                elif mykey[0:3] == 'del':
                    pname=mykey[4:]
                    try:
                        p=Param.objects.get(name=pname)
                        p.delete()
                        deleted.append(pname)
                        logging.info('Deleted parameter %s from %s'%(pname,self.component))
                    except:
                        logging.info(
                          'Attempt to delete parameter %s for component %s failed '%(
                              pname,self.component))
                else:
                    if mykey not in self.keys:
                        logging.info(
                        'Unexpected key %s ignored in PropertyForm (%s)'%(
                        mykey,self.keys))
                    else:
                        if mykey not in deleted:
                            pname=self.rows[self.keys[mykey]].name
                            p=self.params.filter(name=pname)
                            if len(p)!=1:
                                logging.info('Unexpected queryset length for %s'%pname)
                            new=p[0]
                            new.value=qdict[key]
                            new.save()
