# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.utilities import tabs

from django import forms
import logging

class linker:
    ''' Used to tell the form what to do about making links to references '''
    def __init__(self,resource):
        self.resource

class MyRefForm(ReferenceForm):
    ''' Subclassed to ensure we get extra attributes and right vocab '''
    def __init__(self,cid,r,*args,**kwargs):
        self.vocab=Vocab.objects.get(name='Reference Types Vocab')
        ReferenceForm.__init__(self,instance=r,*args,**kwargs)
        self.MyEditURL=reverse
        if r is None:
            self.MyEditURL=reverse('cmip5q.protoq.views.referenceEdit',
                args=(cid,))
        else:
            self.MyEditURL=reverse('cmip5q.protoq.views.referenceEdit',args=(cid,r.id,))
        self.fields['refType'].queryset=Value.objects.filter(vocab=self.vocab)
    def save(self,*args,**kwargs):
        r=ReferenceForm.save(self,*args,**kwargs)
        r.refTypes=self.vocab
        return r

class referenceHandler:
    ''' Handles questionnaire references '''
    def __init__(self,centre_id=None):
        ''' Initialise reference handler'''
        self.cid=centre_id
        self.refs=Reference.objects.all()
        
        if centre_id is None:
            t='None'
        else:
            t=tabs(centre_id,'Refs')
        self.tabs=t
    
    def render(self,linkURL=0,unlinkURL=0):
        rforms=[]
        for r in self.refs:
            rform=MyRefForm(self.cid,r)
            rforms.append(rform)
        rform=MyRefForm(self.cid,None)
        rforms.append(rform)
        return render_to_response('references.html',{'rforms':rforms,
                                  'tabs':self.tabs,
                                  'linkURLbase':linkURL,
                                  'unlinkURLbase':unlinkURL})
    def list(self):
        ''' Provide a list of references '''
        return self.render()
        
    
    def edit(self,request,ref_id=None,ajax=0):
        ''' Edit or add a new request to the reference set. '''
        # if part, simply create it, let a calling routine do the rendering
        logging.debug('Edit reference  [%s]'%ref_id)
        if ref_id is None:
            r=None
            url=reverse('cmip5q.protoq.views.referenceEdit',args=(self.cid,))
        else: 
            r=Reference.objects.get(id=ref_id)
            reverse('cmip5q.protoq.views.referenceEdit',args=(self.cid,ref_id,))
            
        if request.method=='POST':
            #incoming form ...
            rform=MyRefForm(self.cid,r,request.POST)
            if rform.is_valid():
                r=rform.save()
                url=reverse('cmip5q.protoq.views.referenceEdit',args=(self.cid,r.id,))
                if not ajax:return HttpResponseRedirect(url)
                rform=MyRefForm(self.cid,r)
        else:   
            rform=MyRefForm(self.cid,r)
        return render_to_response('reference.html',{'r':rform})
        
    def unlink(self,resource,ref_id):
        ''' Provide a reference list, which submits to a method on the resource
        which unlinks '''
        pass
    
    def link(self,resource,ref_id):
        ''' Provid a reference list, which submits to a method on the resource
        which links '''
        pass
    
    