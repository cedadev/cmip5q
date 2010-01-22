from lxml import etree as ET
from django.shortcuts import render_to_response
from django.http import HttpResponse

class cimHandler(object):
    ''' This is a base class to allow common xml and export related views '''
    
    def __init___(self):
        ''' Sublasses need to instantiate Klass and pkid attributes '''
        pass
    
    def validate(self):
        ''' Is this object complete? '''
        obj=self.Klass.objects.get(pk=self.pkid)
        valid,html=obj.validate()
        return render_to_response('validation.html',{'sHTML':html,'cimHTML':''})
    
    def view(self):
        ''' Return a "pretty" version of self '''
        return self.HTML()
      
    def HTML(self):
        html=viewer(self.XML())
        return HttpResponse(html)
    
    def XMLO(self):
        ''' XML view of self as an lxml element tree instance '''
        obj=self.Klass.objects.get(pk=self.pkid)
        return obj.xmlobject()

    def XMLasHTML(self):
        #docStr=ET.tostring(CIMDoc,"UTF-8")
        mimetype='application/xml'
        docStr=ET.tostring(self.XMLO(),pretty_print=True)
        return HttpResponse(docStr,mimetype)

