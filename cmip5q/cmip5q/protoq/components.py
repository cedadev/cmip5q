# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import PropertyForm,tabs
from cmip5q.XMLVocabReader import XMLVocabReader

from django import forms
import uuid
import logging

import os

#FIXME: change to the simpler way it's done in Platforms.
class MyCouplingForm(CouplingForm):
    ''' Subclassed to ensure we get extra attributes and right vocabs '''
    def __init__(self,cenid,comid,r,*args,**kwargs):
        CouplingForm.__init__(self,instance=r,*args,**kwargs)
        self.vocabs={'couplingType':Vocab.objects.get(name='couplingType'),
                     'couplingFreq':Vocab.objects.get(name='couplingFreq'),
                     'couplingInterp':Vocab.objects.get(name='couplingInterp'),
                     'couplingDim':Vocab.objects.get(name='couplingDim')}
        if r is None:
            self.MyEditURL=reverse('cmip5q.protoq.views.componentCup',
                args=(cenid,comid,))
        else:
            self.MyEditURL=reverse('cmip5q.protoq.views.referenceEdit',args=(cenid,comid,r.id,))
        for f in self.vocabs:
            self.fields[f].queryset=Value.objects.filter(vocab=self.vocabs[f])

def makeComponent(centre_id,scienceType='sub'):
    ''' Just make and return a new component instance'''
    centre=Centre.objects.get(pk=centre_id)
    #ok create a new component
    u=str(uuid.uuid1())
    c=Component(scienceType=scienceType,centre=centre,abbrev='',uri=u)
    #now save to database so that we get a primary key value
    c.save()
    logging.info('Created new component %s in centre %s (type %s)'%(c.id,centre_id,scienceType))
    return c
    
class componentHandler(object):
    # Data directory for retrieving mindmap XML files
    mindMapDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'data',
                              'mindmaps')
    
    def __init__(self,centre_id,component_id=None):
        ''' Instantiate a component handler, by loading existing component information '''
        
        self.centre_id=centre_id
        self.id=component_id
        
        if component_id is None:
            ''' This is a brand new component '''
            component=makeComponent(centre_id,scienceType='model')
            authorN='joe bloggs'
            authorE='bnl@foo.bar'  # FIXME
            component.email=authorE
            component.contact=authorN
            component.title='GCM Template'
            component.abbrev='GCM Template'
            mindmaps=[os.path.join(componentHandler.mindMapDir, f) 
                      for f in os.listdir(componentHandler.mindMapDir)
                      if f.endswith('.xml')]
            for m in mindmaps:
                x=XMLVocabReader(m, centre_id,authorN,authorE)
                x.doParse()
                xx=Component.objects.get(pk=x.topLevelID)
                component.components.add(xx)
                #don't know why I have to use the real component instead of ID here.
                logging.debug('Mindmap %s added with component id %s'%(m,x.topLevelID))
            component.save()
            logging.info('Created new component %s in centre %s'%(component.id,centre_id)) 
            for x in component.components.all(): logging.debug('...component includes %s'%x.abbrev)
            component_id=component.id
        
        self.tabs=tabs(centre_id,'Update')
        self.component=Component.objects.get(pk=component_id)
    
    def add(self):
        '''Add a new root component, essentially all we need to do is return a redirection to an edit '''
        url=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,self.component.id,))
        return HttpResponseRedirect(url)
            
    def addsub(self):
        ''' Add a subcomponent to a parent, essentially, we create a subcomponent, and return
        it for editing  '''
        #we have instantiated self.component as the parent!
        component=makeComponent(self.centre_id,scienceType='sub')
        #default should be that children inherit parents contact.
        component.contact=self.component.contact
        component.abbrev='unknown'
        component.save()
        self.component.components.add(component)
        url=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,component.id,))
        logging.info('Created subcomponent %s to component %s'%(component.id,self.component.id))
        return HttpResponseRedirect(url)

    def edit(self,request):
        ''' Provides a form to edit a component, and handle the posting of a form
        containing edits for a component '''
        
        c=self.component
        logging.debug('Starting editing component %s'%c.id)
        
        # find my own urls ...
        urls={}
        urls['form']=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,c.id,))
        urls['refs']=reverse('cmip5q.protoq.views.assignReferences',args=(self.centre_id,'component',c.id,))
        urls['outputs']=reverse('cmip5q.protoq.views.componentOut',args=(self.centre_id,c.id,))
        urls['subcomp']=reverse('cmip5q.protoq.views.componentSub',args=(self.centre_id,c.id,))
        urls['numerics']=reverse('cmip5q.protoq.views.componentNum',args=(self.centre_id,c.id))
        urls['coupling']=reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,c.id))
        urls['view']=reverse('cmip5q.protoq.views.componentValidate',args=(self.centre_id,c.id))
        urls['validate']=reverse('cmip5q.protoq.views.componentView',args=(self.centre_id,c.id))
        
        baseURL=reverse('cmip5q.protoq.views.componentAdd',args=(self.centre_id,))
        template='+EDID+'
        baseURL=baseURL.replace('add/','%s/edit'%template)
        
        # now get parent, if available 
        # and monkey patch it in, all monkey patching to use prefix TC ...
        parents=Component.objects.filter(components=c.id)
        if len(parents)==0: 
            c.TCparentID=None
        else: 
            c.TCparentID=parents[0].id
            c.TCparentAbbrev=parents[0].abbrev
        logging.debug('editing component %s which has parent %s'%(c.id,c.TCparentID))
        # now get subcomponents
        subc=c.components.all()
    
        # this is the automatic machinery ...
        refs=Reference.objects.filter(component__id=c.id)
        
        #am I a realm level component?
        realms=[str(i) for i in Value.objects.filter(vocab=Vocab.objects.get(name="Realms"))]
        if c.scienceType in realms:
            realm=1
        else:realm=0
        
        pform=PropertyForm(c,prefix='props')
        postOK=True
        if request.method=="POST":
            cform=ComponentForm(request.POST,prefix='gen',instance=c)
            if cform.is_valid():
                uricopy=c.uri
                c=cform.save(commit=False)
                #these are all the bits not in the form ...
                c.uri=uricopy
                c.save()
                logging.debug('Saving component %s details (e.g. uri %s)'%(c.id,c.uri))
            else:
                logging.debug('Unable to save characteristics for component %s'%c.id)
                postOK=False
            pform.update(request)
        
        # We separate the response handling so we can do some navigation in the
        # meanwhile ...
        navtree=yuiTree2(c.id,baseURL,template=template)
        
        #OK, we have three cases to handle:
        
        #FIXME; we'll need to put this in the right places with instances:
    
        if request.method=='POST':
            if postOK:
                #redirect, so repainting the page doesn't resubmit
                logging.debug('Finished handling post to %s'%c.id)
                return HttpResponseRedirect(urls['form'])
            else:
                pass
                # don't reset the forms so the user gets an error response.
        else:
            #get some forms
            cform=ComponentForm(instance=c,prefix='gen')
    
        logging.debug('Finished handling %s to component %s'%(request.method,c.id))
        return render_to_response('componentMain.html',
                {'c':c,'subs':subc,'refs':refs,
                'cform':cform,'pform':pform,
                'navtree':navtree.html,
                'urls':urls,
                'realm':realm,
                'tabs':self.tabs,'notAjax':not request.is_ajax()})
            
    def manageRefs(self,request):      
        ''' Handle references for a specific component '''
        refs=Reference.objects.filter(component__id=self.component.id)
        allrefs=Reference.objects.all()
        available=[]
        c=self.component
        for r in allrefs: 
            if r not in refs:available.append(r) 
        rform=ReferenceForm()
        refu=reverse('cmip5q.protoq.views.addReference',args=(self.centre_id,c.id,))
        baseURLa=reverse('cmip5q.protoq.views.assignReference',args=(1,1,))[0:-4]
        baseURLr=reverse('cmip5q.protoq.views.remReference',args=(1,1,))[0:-4]
        return render_to_response('componentRefs.html',
            {'refs':refs,'available':available,'rform':rform,'c':c,
            'refu':refu,'baseURLa':baseURLa,'baseURLr':baseURLr,
            'tabs':self.tabs,'notAjax':not request.is_ajax()})
            
    def validate(self):
        ''' Validate component '''
        return HttpResponse('Not implemented')
    
    def view(self):
        ''' HTML view of self '''
        return HttpResponse('Not implemented')
    
    def XML(self):
        ''' XML view of self '''
        return HttpResponse('Not implemented')
   
    def numerics(self):
        return HttpResponse('Not implemented')
        
    def coupling(self,request):
        ''' There should be at most one coupling per component '''
        coupling=None
        if request.method=='POST':
            pass
        elif request.method=='GET':
            cform=MyCouplingForm(self.centre_id,self.component.id,coupling)
        return render_to_response('coupling.html',{'c':self.component,'cform':cform})
    
    def outputs(self):
        return HttpResponse('Not implemented')
        
        
