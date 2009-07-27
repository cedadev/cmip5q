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

class MyConformanceForm(ConformanceForm):
    ''' Handles requirements specificity '''
    def __init__(self,*args,**kwargs):
        ConformanceForm.__init__(self,*args,**kwargs)
    def specialise(self,centre):
        # FIXME, we should make this queryset include just component within a specific model
        self.fields['component'].queryset=Component.objects.filter(centre=centre)

class MySimForm(SimulationForm):
    ''' Handles specific issues for a SimulationForm '''
    def __init__(self,*args,**kwargs):
        SimulationForm.__init__(self,*args,**kwargs)
    def centre(self,centre):
        self.fields['platform'].queryset=Platform.objects.filter(centre=centre)
        self.fields['numericalModel'].queryset=Component.objects.filter(scienceType='model').filter(centre=centre)
        

class simulationHandler(object):
    
    def __init__(self,centre_id,simid=None,expid=None):
        ''' Initialise based on what the request needs '''
        self.centreid=centre_id
        self.centre=Centre.objects.get(pk=centre_id)
        self.simid=simid
        self.expid=expid
        
    def __conformances(self,s,reqs):
        ''' We monkey patch onto the requirments what is needed to put up a conformance
        form as well '''
        
        class conform:
            def __init__(self,url,form):
                self.url=url
                self.form=form
        
        for r in reqs:
            # attach variables for a conformance request form
            # need an id, a url, and a form 
            url=reverse('cmip5q.protoq.views.conformanceEdit',args=(self.centreid,s.id,r.id))
            form=MyConformanceForm()
            form.specialise(s.centre)
            r.con=conform(url,form)
            
        return reqs
        
    def __handle(self,request,s,e,url,label):
        ''' This method handles the form itself for both
        the add and edit methods '''
        
        
        reqs=e.requirements.all()
        
        editURL=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,s.id))
        dataurl=reverse('cmip5q.protoq.views.dataEdit',args=(self.centreid))
        print 'dataurl',dataurl
        
        if label=="Update": reqs=self.__conformances(s,reqs)
        
        if request.method=='POST':
            simform=MySimForm(request.POST,instance=s)
            simform.centre(self.centre)
            if simform.is_valid():
                s=simform.save()
                
                return HttpResponseRedirect(editURL)
            else:
                print 'SIMFORM not valid [%s]'%simform.errors
        else:
          
            simform=MySimForm(instance=s)
            simform.centre(self.centre)
        
        return render_to_response('simulation.html',
            {'simform':simform,'url':url,'label':label,'exp':e,'reqs':reqs,'dataURL':dataurl,
            'notAjax':not request.is_ajax()})
        
        
    def edit(self,request):
        ''' Handle providing and receiving edit forms '''
       
        s=Simulation.objects.get(pk=self.simid)
        e=s.experiment
        url=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,s.id,))
        label='Update'
        return self.__handle(request,s,e,url,label)
       
            
    def add(self,request):
        ''' Create a new simulation instance '''
        # first see whether a model and platform have been created!
        # if not, we should return an error message ..
        c=self.centre
        p=c.platform_set.values()
        m=c.component_set.values()
        url=reverse('cmip5q.protoq.views.centre',args=(self.centreid,))
        if len(p)==0:
            ''' Require them to create a platform '''
            message='You need to create a platform before creating a simulation'
            return render_to_response('error.html',{'message':message,'url':url})
        elif len(m)==0:
            ''' Require them to create a model'''
            message='You need to create a model before creating a simulation'
            return render_to_response('error.html',{'message':message,'url':url})
        url=reverse('cmip5q.protoq.views.simulationAdd',args=(self.centreid,self.expid,))
        u=str(uuid.uuid1())
        e=Experiment.objects.get(pk=self.expid)
        s=Simulation(uri=u,experiment=e,centre=self.centre)
        label='Add'
        return self.__handle(request,s,e,url,label)
        
    def validate(self):
        ''' Is this simulation complete? '''
        return HttpResponse('Not implemented')
    
    def view(self):
        ''' Return a "pretty" version of self '''
        return HttpResponse('Not implemented')
      
    def list(self,request):
        ''' Return a listing of simulations for a given centre '''
        
        c=Centre.objects.get(pk=self.centreid)
        exp=[]
        
        #little class to monkey patch up the stuff needed for the template
        class etmp:
            def __init__(self,abbrev,values,id):
                self.abbrev=abbrev
                self.values=values
                self.id=id
                self.new=reverse('cmip5q.protoq.views.simulationAdd',args=(c.id,id,))
                
        for e in Experiment.objects.all():
            sims=[s for s in e.simulation_set.filter(centre=c.id)]
            for s in sims: s.url=reverse('cmip5q.protoq.views.simulationEdit',args=(c.id,s.id,))
            exp.append(etmp(e.docID,sims,e.id))
            print 'loading experiment %s (%s)'%(e.id,e.docID)
        
        logging.info('Viewing simulation %s'%c.id)
        
        return render_to_response('simulationList.html',
            {'c':c,'experiments':exp,
            'tabs':tabs(c.id,'Simulations'),'notAjax':not request.is_ajax()})
        