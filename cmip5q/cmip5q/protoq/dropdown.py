## http://dropdown-check-list.googlecode.com/svn/trunk/src/demo.html
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
logging=settings.LOG

SCRIPT='''<script type="text/javascript">$("#id_%s").dropdownchecklist({%s});</script>'''
SCRIPT2='''<script type="text/javascript">$("#id_%s").dropdownchecklist({%s});</script>'''

def displayAttributes(**kwargs):
    if 'attrs' in kwargs:
        a=kwargs['attrs']
    else: a={}
    if 'maxDropHeight' not in a: a['maxDropHeight']=200
    if 'size' in a:
        # hack to get from "django" size to something appropriate for a screen
        a['width']=int(a['size'])*6  
        del(a['size'])
    logging.debug(str(a))
    return ','.join(['%s:%s'%(k,a[k]) for k in a]) 

class DropDownWidget(forms.SelectMultiple):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.SelectMultiple.__init__(self,*args,**kwargs)
        self.stratt=displayAttributes(**kwargs)
    def render(self,name, value, attrs):
        s=forms.SelectMultiple.render(self,name,value,attrs)
        s+=mark_safe(SCRIPT%(name,self.stratt))
        return s
    
class DropDownSingleWidget(forms.Select):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.Select.__init__(self,*args,**kwargs)
        self.stratt=displayAttributes(**kwargs)
    def render(self,name, value, attrs):
        s=forms.Select.render(self,name,value,attrs)
        s+=mark_safe(SCRIPT%(name,self.stratt))  # not sure I think I really like these ...
        return s

