import logging
from cmip5q.protoq.models import *

class ParamRow(object):
    
    ''' used to monkey patch our special parameter forms '''
    
    def __init__(self,name):
        self.name=name 

class PropertyForm:
    
    ''' this class instantiates the form elements needed by a component view
    of questionnaire properties aka parameters '''
    
    def __VocabRowHTML(self,name,ptype,values):
        ''' return the html for a vocab row '''
        operation={'OR':'+=','XOR':'='}[ptype]
        advice={'OR':'Multiple','XOR':'One'}[ptype]
        logging.info('Arguments to row %s,%s,%s'%(name,operation,len(values)))
        html='''<tr>
             <td>%s</td><td><input name="%s" id="id_%s"></td>
             <td><select name="opt_%s" size="1" onchange="document.getElementById(\'id_%s\').value %s this.value + \'|\';">'''%(name, name, name, name, name, operation)
        for v in values:
            html+='<option value="%s">%s</option>'% (v.value, v.value)
        html+='</select></td><td>%s</td></tr>'%advice
        return html
    
    def __init__(self,component,prefix=''):
        
        #FIXME:
        if prefix<>'': logging.debug("PropertyForm doesn't handle prefixes properly!")
        
        # filter chaining, see
        # http://docs.djangoproject.com/en/dev/topics/db/queries/#chaining-filters
        params=Param.objects.filter(component=component)
        self.orp=params.filter(ptype='OR')
        self.xorp=params.filter(ptype='XOR')
        self.other=params.exclude(ptype='OR').exclude(ptype='XOR')
        
        self.rows=[]
        
        for o in self.orp:
            pp=ParamRow(o.name)
            values=Value.objects.filter(vocab=o.vocab)
            pp.html=self.__VocabRowHTML(o.name,'OR',values)
            self.rows.append(pp)
        
        for o in self.xorp:
            pp=ParamRow(o.name)
            values=Value.objects.filter(vocab=o.vocab)
            pp.html=self.__VocabRowHTML(o.name,'XOR',values)
            self.rows.append(pp)
            
        
          
        
                  
        
        
        
        
        
    