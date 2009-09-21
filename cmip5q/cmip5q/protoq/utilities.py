import logging
from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse

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


class tabs(list):
    ''' Build a list of tabs to be used on each page, passed to base.html '''
    def __init__(self,centre_id,active):
        list.__init__(self)
        t={}
        c=Centre.objects.get(id=centre_id)
        t['Sum']=tab('Home:%s'%c.abbrev,
                reverse('cmip5q.protoq.views.centre',args=(centre_id,)))
        self.append(t['Sum'])
        models=[Component.objects.get(pk=m.id) for m in c.component_set.filter(scienceType='model')]
        for m in models:
            t[m.abbrev]=tab(m.abbrev,
                reverse('cmip5q.protoq.views.componentEdit',args=(centre_id,m.id,))) 
            self.append(t[m.abbrev])
        t['Sims']=tab('Simulations',
                reverse('cmip5q.protoq.views.simulationList',args=(centre_id,)))
        t['Refs']=tab('References',
                reverse('cmip5q.protoq.views.referenceList',args=(centre_id,)))
        t['Files']=tab('Files',
                reverse('cmip5q.protoq.views.list',args=(centre_id,'file',)))
                #reverse('cmip5q.protoq.views.dataList',args=(centre_id,)))
        t['Help']=tab('Help',
                reverse('cmip5q.protoq.views.help',args=(centre_id,)))
        t['About']=tab('About',
                reverse('cmip5q.protoq.views.about',args=(centre_id,)))
        if active in t.keys(): 
            t[active].activate()
        else:
            t['Extra']=tab(str(active),'',1)
       
        for key in ('Sims','Files','Refs'):self.append(t[key])
        if 'Extra' in t.keys(): self.append(t['Extra'])
        for key in ('Help','About'): self.append(t[key])
       
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
        
        self.rows=[]
        self.keys={}
        
        for o in self.orp:
            o.form={'type':'OR','op':'+='}
            o.form['values']=Value.objects.filter(vocab=o.vocab)
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
        
        for o in self.xorp:
            o.form={'type':'XOR','op':'='}
            o.form['values']=Value.objects.filter(vocab=o.vocab)
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
            
        for o in self.other:
            o.form={'type':'key'}
            self.rows.append(o)
            self.keys[o.name]=len(self.rows)-1
            
                        
    def update(self,request):
        ''' Update a parameter field based on a form posted inwards '''
        qdict=request.POST
        lenprefix=len(self.prefix)
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
                else:
                    if mykey not in self.keys:
                        logging.info(
                        'Unexpected key %s ignored in PropertyForm (%s)'%(
                        mykey,self.keys))
                    else:
                        pname=self.rows[self.keys[mykey]].name
                        p=self.params.filter(name=pname)
                        if len(p)!=1:
                            logging.info('Unexpected queryset length for %s'%pname)
                        new=p[0]
                        new.value=qdict[key]
                        new.save()
