# -*- coding: utf-8 -*-
from django.conf import settings

from django.core.urlresolvers import reverse
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
import uuid

logging=settings.LOG

class HTMLdate:
    ''' Handle an HTML date and convert h,m,d into seconds. Used as a mixin class to aid
    serialisation etc, and usable in other applications too '''
    def __init__(self):
        pass
    def fromstr(self,string):
        '''Load from an HTML encoded string'''
        #1960-09-01T00:00:00Z
        # or -19000-01-01T00:00:00Z
        try:
            d,t=string.strip().split('T')
            bits=d.split('-')
            if len(bits)==3:
                self.yyyy,self.mm,self.dd=bits
            else: 
                self.yyyy,self.mm,self.dd=bits[1:]
                self.yyyy='-'+self.yyyy
            h,m,s=t.split(':')
            ss=int(h)*3600+int(m)*60+int(s[0:-1])# get rid of trailing Z
        except Exception,e:
            raise ValueError('Not a valid HTML time date "%s" (%s)'%(string,e))
    def tostr(self):
        '''Serialise to an HTML encoded string '''
        h=self.ss/3600
        hs=h*3600
        m=(self.ss-hs)/60
        s=self.ss-(hs+m*60)
        return '%s-%s-%sT%s-%s-%sZ'%(self.yyyy,self.mm,self.dd,h,m,s)
       
def atomuri():
    ''' Return a uri, put here in one place ... just in case '''
    return '%s'%uuid.uuid1()

def render_badrequest(template,variables):
    """
    Returns a HttpResponseBadRequest whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    
    httpresponse_kwargs = {'mimetype':'text/html'}
    
    return HttpResponseBadRequest(loader.render_to_string(template,variables), **httpresponse_kwargs)

def gracefulNotFound(method):
    ''' Used to decororate view methods to handle not found gracefully '''
    def trap(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except ObjectDoesNotExist,e:
            return render_badrequest('error.html',{'message':e})
    return trap

def RemoteUser(request,document):
    ''' Assign a metadata maintainer if we have one '''
    key='REMOTE_USER'
    #if key in request.META:
        #user=request.META[key]
        #document.metadataMaintainer=ResponsibleParty( ...)
        #document.save()
    return document

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

