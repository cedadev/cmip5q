# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory

from cmip5q.protoq.models import *
from cmip5q.protoq.forms import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import RemoteUser,atomuri
from cmip5q.protoq.layoutUtilities import tabs
from cmip5q.NumericalModel import NumericalModel
from cmip5q.protoq.coupling import MyCouplingFormSet

from cmip5q.protoq.Translator import Translator
from cmip5q.protoq.cimHandler import cimHandler, commonURLs

from django import forms
from django.conf import settings
logging=settings.LOG

import os
# move from ElementTree to lxml.etree
#from xml.etree import ElementTree as ET
from lxml import etree as ET

import tempfile

ComponentInputFormSet=modelformset_factory(ComponentInput,form=ComponentInputForm,exclude=('owner','realm'),can_delete=True)
            
            
class MyComponentInputFormSet(ComponentInputFormSet):
    def __init__(self,component,realm=False,data=None):
        self.component=component
        if realm:
            qset=ComponentInput.objects.filter(realm=component)
        else:
            qset=ComponentInput.objects.filter(owner=component)
        ComponentInputFormSet.__init__(self,data,queryset=qset)
    def specialise(self):
        ''' No local specialisation, yet '''
        pass
    def __getCouplingGroup(self):
        ''' Local method to get the appropriate coupling group '''
        cgroupset=self.component.model.couplinggroup_set.all()
        assert(len(cgroupset)<>0,'All models should have a coupling group, but what about %s'%self.component.model)
        cg=cgroupset.get(simulation=None)
        return cg
        
    def save(self):
        ''' Loop over form instances, add extra material, and couplings as necessary'''
        instances=ComponentInputFormSet.save(self,commit=False)
        for i in instances:
            i.owner=self.component
            i.realm=self.component.realm
            newCoupling=0
            if i.id is None:
                #This is a new instance, and we need to create a coupling for it
                #at the same time. Actually doing this makes me realise we could to
                #back to creating couplings at input declaration time. THey're the
                #same thing. However, the reason for separating them is about when
                #we interact with them.
                newCoupling=1
            i.save()
            if newCoupling:
                c=Coupling(parent=self.__getCouplingGroup(),targetInput=i)
                c.save()
    
class componentHandler(object):
    
    def __init__(self,centre_id,component_id=None):
        ''' Instantiate a component handler, by loading existing component information '''
        
        self.centre_id=centre_id
        self.pkid=component_id
        self.Klass='Unknown by component handler as yet'
        
        if component_id is None:
            ''' This is a brand new component '''
            #nm=NumericalModel(0,centre=Centre.objects.get(id=centre_id))
            #nm.read()
            cmip5c=Centre.objects.get(abbrev='CMIP5')
            original=Component.objects.filter(abbrev='GCM Template').get(centre=cmip5c)
            self.component=original.copy(Centre.objects.get(id=centre_id))
        else:
            try:
                self.component=Component.objects.get(id=component_id)
                self.Klass=self.component.__class__
            except Exception,e:
                logging.debug('Attempt to open an unknown component %s'%component_id)
                raise Exception,e
        
        self.url=reverse('cmip5q.protoq.views.componentEdit',
                         args=(self.centre_id,self.component.id))
       
            
    def XMLasText(self):
        # FIXME: split this into model and view activities ...
        translator=Translator()
        c=self.component  # and move to cimHandler
        htmlDoc=translator.c2text(c)
        html=ET.tostring(htmlDoc)
        return render_to_response('text.html',{'HTML':html})
    
    
    def addsub(self,request):
        ''' Add a subcomponent to a parent, essentially, we create a subcomponent, and return
        it for editing  '''
        #we have instantiated self.component as the parent!
        #ok create a new component
        if request.method=='POST':
            u=atomuri()
            c=Component(scienceType='sub',centre=self.component.centre,uri=u,abbrev='new',
                        contact=self.component.contact,author=self.component.author,
                        funder=self.component.funder,
                        model=self.component.model,realm=self.component.realm)
            r=c.save()
            p=ParamGroup()
            p.save()
            c.paramGroup.add(p) 
            cg=ConstraintGroup(constraint='',parentGroup=p)
            cg.save()
            #print 'Return Value',r
            self.component.components.add(c)
            url=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,c.id,))
            logging.info('Created subcomponent %s in component %s (type "new")'%(c.id,self.component.id))
            return HttpResponseRedirect(url)
        else:
            #would be better to post the create child to the parent url, not this artificial non restful way 
            return HttpResponseBadRequest('Cannot use HTTP GET to this URL')

    def edit(self,request):
        ''' Provides a form to edit a component, and handle the posting of a form
        containing edits for a component, or a delete'''
        
        c=self.component
        logging.debug('Starting editing component %s'%c.id)
        
        if request.method=='POST':
            if 'deleteMe' in request.POST:
                if c.controlled:
                    logging.debug('Invalid delete POST to controlled component')
                    return HttpResponse('Invalid Request')
                else:
                    if len(c.components.all())<>0:
                        return HttpResponse('You need to delete child components first')
                    parent=Component.objects.filter(components=c)[0]
                    url=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,parent.id,))
                    c.delete()
                    return HttpResponseRedirect(url)
        
        # find my own urls ...
        urls={}
        urls['form']=self.url
        urls['refs']=reverse('cmip5q.protoq.views.assign',args=(self.centre_id,'reference',
                             'component',c.id,))
        urls['subcomp']=reverse('cmip5q.protoq.views.componentSub',args=(self.centre_id,c.id,))
        urls['coupling']=reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,c.id))
        urls['inputs']=reverse('cmip5q.protoq.views.componentInp',args=(self.centre_id,c.id))
        urls['text']=reverse('cmip5q.protoq.views.componentTxt',args=(self.centre_id,c.id))
        
        urls=commonURLs(c.model,urls)
        
        baseURL=reverse('cmip5q.protoq.views.componentAdd',args=(self.centre_id,))
        template='+EDID+'
        baseURL=baseURL.replace('add/','%s/edit'%template)
    
        # this is the automatic machinery ...
        refs=Reference.objects.filter(component__id=c.id)
        inps=ComponentInput.objects.filter(owner__id=c.id)
        
        pform=NewPropertyForm(c,prefix='props')
        
        postOK=True
        if request.method=="POST":
            cform=ComponentForm(request.POST,prefix='gen',instance=c)
            if cform.is_valid():
                c=cform.save()
                c=RemoteUser(request,c)
                logging.debug('Saving component %s details (e.g. uri %s)'%(c.id,c.uri))
            else:
                logging.debug('Unable to save characteristics for component %s'%c.id)
                postOK=False
                logging.debug(cform.errors)
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
        
        if c.isModel:
            #we'd better decide what we want to say about couplings. Same code in simulation!
            cset=c.couplings(None)
        else: cset=None
        
        logging.debug('Finished handling %s to component %s'%(request.method,c.id))
        return render_to_response('componentMain.html',
                {'c':c,'refs':refs,'inps':inps,
                'cform':cform,'pform':pform,
                'navtree':navtree.html,
                'urls':urls,
                'isRealm':c.isRealm,
                'isModel':c.isModel,
                'cset':cset,
                'tabs':tabs(request,self.centre_id,'Model',self.component.model.id),
                'notAjax':not request.is_ajax()})
            
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
            'tabs':tabs(request,self.centre_id,'References for %s'%c),
            'notAjax':not request.is_ajax()})
        
    def coupling(self,request,ctype=None):
        ''' Handle the construction of component couplings '''
        # we do the couplings for the parent model of a component
        model=self.component.model
        okURL=reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,self.pkid,))
        urls={'self':reverse('cmip5q.protoq.views.componentCup',
                args=(self.centre_id,self.pkid,))
              }
        cg=CouplingGroup.objects.filter(component=model).get(simulation=None)
        if request.method=='POST':
            Intform=MyCouplingFormSet(cg,request.POST)
            if Intform.is_valid():
                Intform.save()
                return HttpResponseRedirect(okURL)
            else:
                Intform.specialise()
        elif request.method=='GET':
            Intform=MyCouplingFormSet(cg)
            Intform.specialise()
        return render_to_response('coupling.html',{'c':model,'urls':urls,
        'Intform':Intform,'tabs':tabs(request,self.centre_id,'Coupling for %s'%c)})
        
    def inputs(self,request):
        ''' Handle the construction of input requirements into a component '''
        okURL=reverse('cmip5q.protoq.views.componentInp',args=(self.centre_id,self.pkid,))
        urls={'ok':okURL,'self':self.url}
        if request.method=='POST':
            Inpform=MyComponentInputFormSet(self.component,self.component.isRealm,
                                            request.POST)
            if Inpform.is_valid():
                Inpform.save()
                return HttpResponseRedirect(okURL)
            else:
                Inpform.specialise()
        elif request.method=='GET':
            Inpform=MyComponentInputFormSet(self.component,self.component.isRealm)  
            Inpform.specialise()
        return render_to_response('inputs.html',{'c':self.component,'urls':urls,
                                   'form':Inpform,
                                   'tabs':tabs(request,self.centre_id,'Inputs for %s'%self.component)})
    
    def copy(self,request):
        ''' Make a copy for later editing. Currently restricted to model components only '''
        # Must be a post ...
        if request.method!='POST':
            return HttpResponse('uknown request')
        if not self.component.isModel: return HttpResponse("Not a model, wont copy")
        centre=Centre.objects.get(id=self.centre_id)
        new=self.component.copy(centre)
        new.abbrev=self.component.abbrev+'cp'
        new.title=self.component.title+'cp'
        new.save()
        url=reverse('cmip5q.protoq.views.componentEdit',args=(self.centre_id,new.id,))
        logging.info('Created new model %s with id %s (copy of %s)'%(new,new.id,self.component))
        return HttpResponseRedirect(url)
