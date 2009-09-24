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
            #nm=NumericalModel(0,centre=Centre.objects.get(id=centre_id))
            #nm.read()
            cmip5c=Centre.objects.get(abbrev='CMIP5')
            original=Component.objects.filter(abbrev='GCM Template').get(centre=cmip5c)
            self.component=original.makeNewCopy(Centre.objects.get(id=centre_id))
        else:
            self.component=Component.objects.get(pk=component_id)
        
        self.url=reverse('cmip5q.protoq.views.componentEdit',
                         args=(self.centre_id,self.component.id))
            
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
    
        # this is the automatic machinery ...
        refs=Reference.objects.filter(component__id=c.id)
        inps=ComponentInput.objects.filter(owner__id=c.id)
        
        pform=PropertyForm(c,prefix='props')
        postOK=True
        if request.method=="POST":
            cform=ComponentForm(request.POST,prefix='gen',instance=c)
            if cform.is_valid():
                c=cform.save()
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

    def validate(self):
        ''' Validate model '''

        # create CIM instance
        my_component=self.component.model # use component for current component
        component_id=my_component.id
        nm=NumericalModel(Centre.objects.get(id=self.centre_id),component_id)
        CIMDoc=nm.export() # add recurse=False to limit to this component only

        #validate against schema
        #CIM currently fails the schema parsing
        #xmlschema_doc = ET.parse("xsd/cim.xsd")
        #xmlschema = ET.XMLSchema(xmlschema_doc)
        #if xmlschema.validate(CIMDoc):
        #  logging.debug("CIM Document validates against the cim schema")
        #else:
        #  logging.debug("CIM Document fails to validate against the cim schema")
        #log = xmlschema.error_log
        #logging.debug("CIM Document schema errors are "+log)

        #validate against schematron checks
        sct_doc = ET.parse("xsl/BasicChecks.sch")
        schematron = ET.Schematron(sct_doc)
        if schematron.validate(CIMDoc):
          logging.debug("CIM Document passes the schematron tests")
        else:
          logging.debug("CIM Document fails the schematron tests")

        #obtain schematron report in html
        xslt_doc = ET.parse("xsl/schematron-report.xsl")
        transform = ET.XSLT(xslt_doc)
        xslt_doc = transform(sct_doc)
        transform = ET.XSLT(xslt_doc)
        schematronhtml = transform(CIMDoc)

        #also generate the cim as html
        xslt_doc = ET.parse("xsl/xmlformat.xsl")
        transform = ET.XSLT(xslt_doc)
        formattedCIMDoc = transform(CIMDoc)
        xslt_doc = ET.parse("xsl/verbid.xsl")
        transform = ET.XSLT(xslt_doc)
        cimhtml = transform(formattedCIMDoc)

        response=HttpResponse('<html><head><title>CIM Validation page</title></head><body><h2>Validate not yet fully implemented</h2><h2>Schematron results</h2><p/>'+str(schematronhtml)+'<h2>CIM XML</h2><p/>'+str(cimhtml)+'</body></html>')
        return response
    
    def view(self):
        ''' HTML view of self '''
        ''' Return a CIM XML view for the moment'''
        return self.XML(mimetype="doc/cim/xml")
    
    def XML(self,mimetype="application/xml"):
        ''' XML view of self'''
        nm=NumericalModel(Centre.objects.get(id=self.centre_id),self.component.model.id)
        CIMDoc=nm.export()
        #docStr=ET.tostring(CIMDoc,"UTF-8")
        docStr=ET.tostring(CIMDoc,pretty_print=True)
        return HttpResponse(docStr,mimetype)

    def XMLasHTML(self,XMLFileName):
        ''' XML view of self supplied in a file and returned as HTML'''
        # prettify the xml file with an xsl stylesheet
        os.system("xsltproc xsl/xmlformat.xsl "+XMLFileName+" > "+XMLFileName+".pretty")
        os.system("mv "+XMLFileName+".pretty "+XMLFileName)

        # create and return html rendered xml using an xsl stylesheet
        error=os.system("xsltproc xsl/xmlverbatim.xsl "+XMLFileName+" > "+XMLFileName+".html")

        # read html file
        file=open(XMLFileName+".html", 'r')
        linestring=file.read()
        file.close()
        os.remove(file.name)

        return linestring
   
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
        'Intform':Intform,'tabs':tabs(request,self.centre_id,'Coupling for %s'%c)})
        
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
                                   'form':Inpform,
                                   'tabs':tabs(request,self.centre_id,'Inputs for %s'%self.component)})
        
    def outputs(self):
        return HttpResponse('Not implemented')
        
        
