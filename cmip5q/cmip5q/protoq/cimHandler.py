from lxml import etree as ET
from django.shortcuts import render_to_response
from django.http import HttpResponse
from protoq.cimHandling import viewer
from django.core.urlresolvers import reverse

def commonURLs(obj,dictionary):
    '''Add urls for the common methods to a dictionary for use in a template '''
    for key in ['validate','view','xml','html','export']:
        dictionary[key]=reverse('cmip5q.protoq.views.genericDoc',args=(obj.centre.id,obj._meta.module_name,obj.id,key))
    return dictionary
    
class cimHandler(object):
    ''' This handles common operations to produce views etc on CIM document objects '''
    
    def __init__(self,obj):
        ''' Instantiate the object '''
        self.obj=obj
        
    def _XMLO(self):
        ''' XML view of self as an lxml element tree instance '''
        return self.obj.xmlobject()  
    
    def validate(self):
        ''' Is this object complete? '''
        valid,html=self.obj.validate()
        return render_to_response('validation.html',{'sHTML':html,'cimHTML':''})
    
    def view(self):
        ''' Return a "pretty" version of self '''
        return self.html()
      
    def html(self):
        html=viewer(self._XMLO())
        return HttpResponse(html)

    def xml(self):
        #docStr=ET.tostring(CIMDoc,"UTF-8")
        mimetype='application/xml'
        docStr=ET.tostring(self._XMLO(),pretty_print=True)
        return HttpResponse(docStr,mimetype)

    def export(self):
        ''' Mark as complete and export to an atom feed '''
        return HttpResponse('not implemented')