from django import forms
from django.utils.safestring import mark_safe

SCRIPT='''<script type="text/javascript">$("#id_%s").dropdownchecklist();</script>'''
SCRIPT2='''<script type="text/javascript">$("#id_%s").dropdownchecklist();</script>'''

class DropDownWidget(forms.SelectMultiple):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.SelectMultiple.__init__(self,*args,**kwargs)
    def render(self,name, value, attrs):
        s=forms.SelectMultiple.render(self,name,value,attrs)
        s+=mark_safe(SCRIPT%name)
        return s
    
class DropDownSingleWidget(forms.Select):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.Select.__init__(self,*args,**kwargs)
    def render(self,name, value, attrs):
        s=forms.Select.render(self,name,value,attrs)
        s+=mark_safe(SCRIPT%name)
        return s

