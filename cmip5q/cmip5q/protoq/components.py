# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import PropertyForm,tabs
from cmip5q.NumericalModel import NumericalModel
from cmip5q.protoq.coupling import MyCouplingFormSet

from django import forms
import uuid
import logging

import os
from xml.etree import ElementTree as ET
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
                c=Coupling(component=self.component.model,
                           targetInput=i)
                c.save()

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
    
    def __init__(self,centre_id,component_id=None):
        ''' Instantiate a component handler, by loading existing component information '''
        
        self.centre_id=centre_id
        self.id=component_id
        
        if component_id is None:
            ''' This is a brand new component '''
            nm=NumericalModel(0,centre=Centre.objects.get(id=centre_id))
            nm.read()
            component=nm.component
            component_id=component.id
        
        self.tabs=tabs(centre_id,'Update')
        self.component=Component.objects.get(pk=component_id)
        self.url=reverse('cmip5q.protoq.views.componentEdit',
                         args=(self.centre_id,self.component.id))
   
    def add(self):
        '''Add a new root component, essentially all we need to do is return a redirection to an edit '''
        return HttpResponseRedirect(self.url)
            
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
        urls['form']=self.url
        urls['refs']=reverse('cmip5q.protoq.views.assignReferences',args=(self.centre_id,'component',c.id,))
        urls['outputs']=reverse('cmip5q.protoq.views.componentOut',args=(self.centre_id,c.id,))
        urls['subcomp']=reverse('cmip5q.protoq.views.componentSub',args=(self.centre_id,c.id,))
        urls['numerics']=reverse('cmip5q.protoq.views.componentNum',args=(self.centre_id,c.id))
        urls['coupling']=reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,c.id))
        urls['inputs']=reverse('cmip5q.protoq.views.componentInp',args=(self.centre_id,c.id))
        urls['view']=reverse('cmip5q.protoq.views.componentView',args=(self.centre_id,c.id))
        urls['validate']=reverse('cmip5q.protoq.views.componentValidate',args=(self.centre_id,c.id))
        
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
        inps=ComponentInput.objects.filter(owner__id=c.id)
        
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
        
        if c.isModel:
            #we'd better decide what we want to say about couplings. Same code in simulation!
            cs=Coupling.objects.filter(component=c).filter(simulation=None)
            cset=[{'name':str(i),'nic':len(InternalClosure.objects.filter(coupling=i)),
                             'nec':len(ExternalClosure.objects.filter(coupling=i)),
                             } for i in cs]
        else: cset=[]
    
        logging.debug('Finished handling %s to component %s'%(request.method,c.id))
        return render_to_response('componentMain.html',
                {'c':c,'subs':subc,'refs':refs,'inps':inps,
                'cform':cform,'pform':pform,
                'navtree':navtree.html,
                'urls':urls,
                'isRealm':c.isRealm,
                'isModel':c.isModel,
                'cset':cset,
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
            
    def getRootComponentID(self,component_id):
        self.component_id=component_id
        parents=Component.objects.filter(components=component_id)
        #logging.debug("getRootComponentID component id = %d",component_id)
        #logging.debug("getRootComponentID num parents = %d",len(parents))
        if len(parents)==1 :
            # recurse to next parent
            self.getRootComponentID(parents[0].id)
        elif len(parents)>1 or len(parents)<0 :
            #error: there should only be 0 or 1 parent
            logging.error("components.py:getRootComponent: There should only be one parent of a component")
        # If the return is part of the above if clause, the type returned is a NoneType. Therefore I've written the method so that the return is at the end
        return self.component_id

    def validate(self):
        ''' Validate component '''

        # find current component
        component_id=self.component.id
        logging.debug("Validate method called for component_id = %d",component_id)
        # find the root component
        root_component_id=self.getRootComponentID(component_id)
        logging.debug("Root component id = %d",root_component_id)

        # create cim instance
        logging.debug("Creating CIM instance from internal state")

        # to create CIM from current component, pass component_id
        # to create CIM from root component, pass root_component_id
        nm=NumericalModel(component_id)
        # nm=NumericalModel(root_component_id)

        # default creates CIM with specified component and all of its children
        # add argument recurse=False to export method to skip any children
        # CIMDoc=nm.export()
        CIMDoc=nm.export(recurse=False)

        # write cim instance to file & stdout
        ET.dump(CIMDoc)
        tree=ET.ElementTree(CIMDoc)
        #I can't seem to get the tempfile class to write a file to disk so perform a silly hack instead ...
        filexxx=tempfile.NamedTemporaryFile(mode='w', suffix='', prefix=self.component.abbrev+"_CIM_")
        file=open(filexxx.name+".xml","w")
        logging.debug("Writing CIM instance to temporary file %s",file.name)
        tree.write(file)

        file.flush()
        return HttpResponse(ET.tostring(CIMDoc))
        #return HttpResponse('Validate is not implemented')
    
    def view(self):
        ''' HTML view of self '''
        component_id=self.component.id;
        logging.debug("Hello from view function")
        return HttpResponse('View is not implemented')
    
    def XML(self):
        ''' XML view of self '''
        return HttpResponse('XML (view) is not implemented')
   
    def numerics(self):
        return HttpResponse('Not implemented')
        
    def coupling(self,request,ctype=None):
        ''' Handle the construction of component couplings '''
        # we do the couplings for the parent model of a component
        model=self.component.model
        okURL=reverse('cmip5q.protoq.views.componentCup',args=(self.centre_id,self.id,))
        urls={'self':reverse('cmip5q.protoq.views.componentCup',
                args=(self.centre_id,self.id,))
              }
                
        if request.method=='POST':
            Intform=MyCouplingFormSet(model,request.POST)
            if Intform.is_valid():
                Intform.save()
                return HttpResponseRedirect(okURL)
            else:
                Intform.specialise()
        elif request.method=='GET':
            Intform=MyCouplingFormSet(model)
            Intform.specialise()
        return render_to_response('coupling.html',{'c':model,'urls':urls,
        'Intform':Intform,'tabs':tabs(self.centre_id,'tmp')})
        
    def inputs(self,request):
        ''' Handle the construction of input requirements into a component '''
        okURL=reverse('cmip5q.protoq.views.componentInp',args=(self.centre_id,self.id,))
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
                                   'form':Inpform,'tabs':tabs(self.centre_id,'tmp')})
        
    def outputs(self):
        return HttpResponse('Not implemented')
        
        
