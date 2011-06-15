from datetime import datetime
import os

from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse
from lxml import etree as ET

from atom import Feed
from cmip5q.protoq.utilities import atomuri, HTMLdate
from cmip5q.protoq.models import CIMObject
from cmip5q.XMLutilities import etTxt


logging=settings.LOG


class TestDocs(object):
    ''' 
        Dummy queryset for test documents
    '''
    
    @staticmethod
    def getdocs(testdir):
        myfiles=[]
        for f in os.listdir(testdir):
            if f.endswith('.xml'): myfiles.append(TestDocumentSet(testdir,f))
        return TestDocs(myfiles)
    
    def __init__(self,myfiles):
        self.myfiles=myfiles
    
    def order_by(self,arg):
        #Just return the list, which probably has only one entry
        return self.myfiles


class TestDocumentSet(object):
    ''' 
        This class provides pseudo CIMObjects from files on disk 
    '''
    
    class DummyAuthor(object):
        def __init__(self):
            self.name='Test Author: Gerry Devine'
            self.email='g.m.devine@met.reading.ac.uk'
            
    def __init__(self, d, f):
        ff = os.path.join(d, f)
        ef = ET.parse(ff)
        cimns = 'http://www.metaforclimate.eu/schema/cim/1.5'
        cimdoclist = ['{%s}modelComponent' %cimns, 
                      '{%s}platform' %cimns, 
                      '{%s}CIMRecord/{%s}CIMRecord/{%s}simulationRun' 
                       %(cimns, cimns, cimns)]
        for cimdoc in cimdoclist:
            if ef.getroot().find(cimdoc) is not None:
                e=ef.getroot().find(cimdoc)
                
        getter=etTxt(e)
        
        #basic document stuff for feed
        doc={'description':'description', 
             'shortName':'abbrev',
             'longName':'title', 
             'documentCreationDate':'created', 
             'updated':'updated', 
             'documentID':'uri'}
        
        for key in doc.keys():
            self.__setattr__(doc[key], getter.get(e, key))
        self.fname = f
        self.cimtype = 'DocumentSet'
        self.author = self.DummyAuthor()
        #if self.created=='':self.created=datetime.now()
        #if self.updated=='':self.updated=datetime.now()
        #FIXME: temporary fix for strange date bug
        self.created = datetime.now()
        self.updated = datetime.now()

    def get_absolute_url(self):
        return reverse('cmip5q.protoq.views.testFile', args=(self.fname, ))


class DocFeed(Feed):
    ''' 
       This is the atom feed for xml documents available from the questionnaire
       See http://code.google.com/p/django-atompub/wiki/UserGuide
    '''
    feeds = {
             'platform': CIMObject.objects.filter(cimtype = 'platform'),
             'simulation': CIMObject.objects.filter(cimtype = 'simulation'),
             'component': CIMObject.objects.filter(cimtype = 'component'),
             'experiment': CIMObject.objects.filter(cimtype = 'experiment'),
             'files': CIMObject.objects.filter(cimtype = 'dataContainer'),
             'all': CIMObject.objects.all(),
             'test': TestDocs.getdocs(settings.TESTDIR)
             }
    
    def _mydomain(self):
        # the request object has been passed to the constructor for the Feed 
        # base class,so we have access to the protocol, port, etc
        current_site = RequestSite(self.request)
        return 'http://%s' %current_site.domain
    
    def _myurl(self, model):
        return self._mydomain() + reverse('django.contrib.syndication.views.feed', 
                                          args=('cmip5/%s'%model,))
    
    def get_object(self, params):
        ''' Used for parameterised feeds '''
        assert params[0] in self.feeds,'Unknown feed request'
        return params[0]
    
    def feed_id (self, model):
        return self._myurl(model)
    
    def feed_title(self, model):
        return 'CMIP5 %s metadata'%model
    
    def feed_subtitle(self,model):
        return 'Metafor questionnaire - completed %s documents'%model
    
    def feed_authors(self,model):
        return [{'name':'The metafor team'}]
    
    def feed_links(self,model):
        u=self._myurl(model)
        return [{"rel": "self", "href": "%s"%u}]
    
    def feed_extra_attrs(self,model):
        return {'xml:base':self._mydomain()}
    
    def items(self,model):
        return self.feeds[model].order_by('-updated')
    
    def item_id(self,item):
        return 'urn:uuid:%s'%item.uri
    
    def item_title(self,item):
        if hasattr(item, "documentVersion"):
            return '%s - Version %s' %(item.title, item.documentVersion)
        else:
            return item.title            
    
    def item_authors(self,item):
        if item.author is not None:
            return [{'name': item.author.name,'email':item.author.email}]
        else: return []
    
    def item_updated(self,item):
        return item.updated
    
    def item_published(self,item):
        return item.created
    
    def item_links(self,item):
        return [{'href':self._mydomain() + item.get_absolute_url()}]
    
    def item_summary(self,item):
        if item.description:
            return item.description
        else:
            return '%s:%s'%(item.cimtype,item.title)
    
    def item_content(self,item):
        ''' Return out of line link to the content'''
        return {"type": "application/xml", "src":item.get_absolute_url()},""