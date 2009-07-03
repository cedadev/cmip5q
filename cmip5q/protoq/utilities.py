import logging
from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse

class tab:
    ''' This is a simple tab class to support yui tabs '''
    def __init__(self,name,url,active=0):
        self.name=name
        self.url=url
        self.active={0:'false',1:'true'}[active]

def tabs(centre_id,view,component=1):
    ''' Build a list of tabs to be used on each page, passed to base.html '''
    t=[]
    t.append(tab('Summary',reverse('cmip5q.protoq.views.centre',args=(centre_id,)),(view=='Summary')))
    t.append(tab('Models',reverse('cmip5q.protoq.views.componentEdit',args=(centre_id,component,)),(view=='Models')))
    t.append(tab('References',reverse('cmip5q.protoq.views.references',args=()),(view=='References')))
    return t

class ParamRow(object):
    
    ''' used to monkey patch our special parameter forms '''
    
    def __init__(self,name):
        self.name=name 

class PropertyForm:
    
    ''' this class instantiates the form elements needed by a component view
    of questionnaire properties aka parameters '''
    
    def __VocabRowHTML(self,name,value,ptype,values):
        ''' return the html for a vocab row '''
        operation={'OR':'+=','XOR':'='}[ptype]
        advice={'OR':'Multiple','XOR':'One'}[ptype]
        logging.info('Arguments to row %s,%s,%s'%(name,operation,len(values)))
        html='''<tr>
             <td>%s</td><td><input name="%s-%s" id="id_%s" size="40" value="%s"></td>
             <td>%s</td><td>
             <select name="opt_%s" size="1" onchange="document.getElementById(\'id_%s\').value %s this.value + \'|\';">'''%(
                name, self.prefix,name,name,value,advice,name, name, operation)
        for v in values:
            html+='<option value="%s">%s</option>'% (v.value, v.value)
        html+='</select></td></tr>'
        return html
    
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
            pp=ParamRow(o.name)
            pp.values=Value.objects.filter(vocab=o.vocab)
            pp.html=self.__VocabRowHTML(o.name,o.value,'OR',pp.values)
            self.rows.append(pp)
            self.keys[o.name]=len(self.rows)-1
        
        for o in self.xorp:
            pp=ParamRow(o.name)
            pp.values=Value.objects.filter(vocab=o.vocab)
            pp.html=self.__VocabRowHTML(o.name,o.value,'XOR',pp.values)
            self.rows.append(pp)
            self.keys[o.name]=len(self.rows)-1
            
        for o in self.other:
            pp=ParamRow(o.name)
            pp.value=o.value
            pp.html='''<tr><td>%s</td><td>
                       <input name="%s-%s" id="id_%s" size="40" value="%s"></td>
                       <td></td><td></td></tr>'''%(
                            o.name,self.prefix,o.name,o.name,o.value)
            self.rows.append(pp)
            self.keys[o.name]=len(self.rows)-1
            
        self.new='''<tr><td><input name="%s-newparam" id="%s-newparam" size="20"></td>
                        <td><input name="%s-newparamval" id="%s-newparamval" size="40"></td>
                        <td></td><td></td></tr>'''%(self.prefix,self.prefix,self.prefix,self.prefix)
                        
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

                        
                        
                        
                        
                        

  