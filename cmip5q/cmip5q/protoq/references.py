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
        dform=[MyRefForm(self.cid,None)]
        print dform[0].MyEditURL
        return render_to_response('references.html',{'rforms':rforms,
                                  'dform':dform,
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
                if not ajax:
                    url=reverse('cmip5q.protoq.views.referenceList',args=(self.cid,))
                    return HttpResponseRedirect(url)
                rform=MyRefForm(self.cid,r)
            else: print rform.errors
        else:   
            rform=MyRefForm(self.cid,r)
        if (ajax):    
            return render_to_response('reference.html',{'r':rform})
        else:
            return render_to_response('referenceAlone.html',{'dform':[rform],'tabs':tabs(self.cid,'Refs')})
        
    def unlink(self,resource,ref_id):
        ''' Provide a reference list, which submits to a method on the resource
        which unlinks '''
        pass
    
    def assign(self,request,resourceType,resource_id):
        ''' Assign references to a specific resource '''
        
        if resourceType=='component':
            res=Component.objects.get(id=resource_id)
            postURL=reverse('cmip5q.protoq.views.componentEdit',args=(self.cid,resource_id))
        # add other things with references to this choice list ...
        
        values=res.references.values()
        print values
        initial=[i['name'] for i in values]
        print 'I',initial
            
        title='Assign references to %s %s'%(resourceType,res)

        data=[(str(r),str(r)) for r in self.refs]
       
        class AssignRefs(forms.Form):
            ''' Used for producing a form for selecting some references '''
            choose=forms.MultipleChoiceField(choices=data,
                          widget=forms.CheckboxSelectMultiple())
                          
        if request.method=='POST':
            rform=AssignRefs(request.POST)
            if rform.is_valid():
                #now parse these up and assign to the resource
                res.references.clear()
                new=rform.cleaned_data['choose']
                for n in new:
                    r=self.refs.get(name=n)
                    res.references.add(r)
                return HttpResponseRedirect(postURL)
        elif request.method=='GET':
            rform=AssignRefs({'choose':initial})
                
        url=reverse('cmip5q.protoq.views.assignReferences',args=(self.cid,resourceType,resource_id,))
        return render_to_response('selectRef.html',
            {'rform':rform,
                'title':title,
                'tabs':tabs(self.cid,'Chooser'),'url':url})
        
                    
            
                 
                 
                 