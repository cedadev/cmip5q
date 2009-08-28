# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.utilities import PropertyForm,tabs

from django import forms
import uuid
import logging


ConformanceFormSet=modelformset_factory(Conformance,exclude=('simulation','requirement'))

class MyConformanceFormSet(ConformanceFormSet):
    ''' Mimics the function of a formset for the situation where we want to edit the
    known conformances '''
    def __init__(self,simulation,data=None):
        self.extra=0
        qset=Conformance.objects.filter(simulation=simulation)
        ConformanceFormSet.__init__(self,data,queryset=qset)
        self.r=[c.requirement.description for c in qset]
        self.s=simulation
    def specialise(self):
        # FIXME: Can't specialise on the code modifications, because we can't get at them
        # should really do it via modifications on this model ... which means we need to
        # have model parent known to all component.
        # FIXME: Can only get to boundary conditions by following the coupling links ...
        # monkey patch some additional information to show on the forms
        if len(self.r)!=len(self.forms):
            raise ValueError('queryset %s and forms %s out of step'%(len(self.r),len(self.forms)))
        v=Vocab.objects.get(name='conformanceTypes')
        for index in range(len(self.r)):
            self.forms[index].req=self.r[index]
            self.forms[index].fields['ctype'].queryset=Value.objects.filter(vocab=v)
    def save(self): 
        instances=ConformanceFormSet.save(self,commit=False)
        for index in range(len(instances)):
            f=instances[index]
            f.simulation=self.s
            f.requirement=self.r[index]
            f.save()
          
class simulationHandler(object):
    
    def __init__(self,centre_id,simid=None,expid=None):
        ''' Initialise based on what the request needs '''
        self.centreid=centre_id
        self.centre=Centre.objects.get(pk=centre_id)
        self.simid=simid
        self.expid=expid
        self.errors={}
        
    def __handle(self,request,s,e,url,label,fix):
        ''' This method handles the form itself for both the add and edit methods '''
        logging.debug('entering simulation handle routine')
        ensemble=0
        
        urls={'url':url}
        if label=='Update':
            urls['ic']=reverse('cmip5q.protoq.views.assign',
                    args=(self.centreid,'simulation',s.id,'initialcondition',))
            urls['bc']=reverse('cmip5q.protoq.views.assign',
                    args=(self.centreid,'simulation',s.id,'boundarycondition'))
            urls['con']=reverse('cmip5q.protoq.views.conformanceMain',
                    args=(self.centreid,s.id,))
            if s.ensembleMembers > 1:
                urls['ens']=reverse('cmip5q.protoq.views.ensemble',
                    args=(self.centreid,s.id,))
                ensemble=PhysicalEnsemble.objects.filter(simulation=s)
        
        if not fix and request.method=='POST':
            # we can't do the following, because on initialisation, we don't know what
            # s.id is for a new simulation
            #editURL=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,s.id))
            afterURL=reverse('cmip5q.protoq.views.simulationList',args=(self.centreid,))
            simform=SimulationForm(request.POST,instance=s)
            simform.specialise(self.centre)
            if simform.is_valid():
                s=simform.save()
                return HttpResponseRedirect(afterURL)
            else:
                print 'SIMFORM not valid [%s]'%simform.errors
        else:
            simform=SimulationForm(instance=s)
            simform.specialise(self.centre)
        
        return render_to_response('simulation.html',
            {'s':s,'simform':simform,'urls':urls,'label':label,'exp':e,
                        'ensemble':ensemble,'tabs':tabs(self.centreid,'Update')})
        
    def edit(self,request,fix=False):
        ''' Handle providing and receiving edit forms '''
       
        s=Simulation.objects.get(pk=self.simid)
        e=s.experiment
        url=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,s.id,))
        label='Update'
        return self.__handle(request,s,e,url,label,fix)
       
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
        return self.__handle(request,s,e,url,label,False)
        
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
            exp.append(etmp(e.longName,sims,e.id))
            print 'loading experiment %s (%s)'%(e.id,e.docID)
        
        logging.info('Viewing simulation %s'%c.id)
        
        return render_to_response('simulationList.html',
            {'c':c,'experiments':exp,
            'tabs':tabs(c.id,'Sims'),'notAjax':not request.is_ajax()})
 
    def conformanceMain(self,request):
        ''' Displays the main conformance view '''

        print 'ss',self.simid
        s=Simulation.objects.get(pk=self.simid)
        e=s.experiment
        
        urls={'self':reverse('cmip5q.protoq.views.conformanceMain',
                    args=(self.centreid,s.id,)),
              'mods':reverse('cmip5q.protoq.views.list',
                    args=(self.centreid,'codemodification','simulation',s.id,)),
              'sim':reverse('cmip5q.protoq.views.simulationEdit',
                    args=(self.centreid,s.id,))
                    }
        con=Conformance.objects.filter(simulation=s)
        if len(con)==0:
            # we need to set up the conformances!
             reqs=e.requirements.all()
             for r in reqs:
                 c=Conformance(requirement=r,simulation=s)
                 c.save()
                 
        if request.method=='POST':
            cformset=MyConformanceFormSet(s,request.POST)
            if cformset.is_valid():
                cformset.save()
                return HttpResponseRedirect(urls['self'])
            else:
                cformset.specialise()
        elif request.method=='GET':
            cformset=MyConformanceFormSet(s)
            cformset.specialise()
          
        return render_to_response('conformance.html',{'s':s,'e':e,'cform':cformset,
                    'urls':urls,'tabs':tabs(self.centreid,'tmp')})
  
    
                