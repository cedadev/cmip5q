from lxml import etree as ET
from django.shortcuts import render_to_response
from django.http import HttpResponse
from cmip5q.protoq.cimHandling import viewer
from django.core.urlresolvers import reverse

def commonURLs(obj,dictionary):
    '''Add urls for the common methods to a dictionary for use in a template '''
    for key in ['validate','xml','html','export']:
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
    
    def _versions(self):
        ''' Provide a list of versions of this CIM document '''
        return HttpResponse('not implemented')
    
    def validate(self):
        ''' Is this object complete? '''
        valid,html=self.obj.validate()
        urls=commonURLs(self.obj,{})
        del urls['validate']  # we've just done it
        return render_to_response('cimpage.html',{'source':'Validation','obj':self.obj,'html':html,'urls':urls})
      
    def html(self):
        ''' Return a "pretty" version of self '''
        html=viewer(self._XMLO())
        urls=commonURLs(self.obj,{})
        del urls['html']
        return render_to_response('cimpage.html',{'source':'View','obj':self.obj,'html':html,'urls':urls})

    def xml(self):
        #docStr=ET.tostring(CIMDoc,"UTF-8")
        mimetype='application/xml'
        docStr=ET.tostring(self._XMLO(),pretty_print=True)
        return HttpResponse(docStr,mimetype)

    def export(self):
        ''' Mark as complete and export to an atom feed '''
        ok,msg,url=self.obj.export()
        html='<p>%s</p>'%msg
        urls=commonURLs(self.obj,{'persisted':url})
        del urls['export']
        return render_to_response('cimpage.html',{'source':'Export to CMIP5','obj':self.obj,'html':html,
                                  'urls':urls})
    
   
    
