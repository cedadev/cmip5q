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


ConformanceFormSet=modelformset_factory(Conformance,
                                        form=ConformanceForm,
                                        exclude=('simulation','requirement'))


class MyConformanceFormSet(ConformanceFormSet):
    ''' Mimics the function of a formset for the situation where we want to edit the
    known conformances '''
    def __init__(self,simulation,data=None):
        self.extra=0
        qset=Conformance.objects.filter(simulation=simulation)
        ConformanceFormSet.__init__(self,data,queryset=qset)
        self.s=simulation
    def specialise(self):
        for form in self.forms:
            form.specialise(self.s)
            
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
        
        if s.ensembleMembers>1:
            eset=s.ensemble_set.all()
            assert(len(eset)==1,'There can only be one ensemble set for %s'%s)
            members=eset[0].ensemblemember_set.all()
            ensemble={'set':eset[0],'members':members}
        else: ensemble=None
        
        urls={'url':url}
        if label=='Update':
            urls['ic']=reverse('cmip5q.protoq.views.assign',
                    args=(self.centreid,'initialcondition','simulation',s.id,))
            urls['bc']=reverse('cmip5q.protoq.views.simulationCup',
                    args=(self.centreid,s.id,))
            urls['con']=reverse('cmip5q.protoq.views.conformanceMain',
                    args=(self.centreid,s.id,))
            urls['ens']=reverse('cmip5q.protoq.views.ensemble',
                    args=(self.centreid,s.id,))
            urls['validate']=reverse('cmip5q.protoq.views.simulationValidate',
                    args=(self.centreid,s.id,))
            urls['view']=reverse('cmip5q.protoq.views.simulationView',
                    args=(self.centreid,s.id,))
            urls['mod']=reverse('cmip5q.protoq.views.assign',
                     args=(self.centreid,'modelmod','simulation',s.id,))
            # dont think we should be able to get to input mods from here ...
            #urls['ics']=reverse('cmip5q.protoq.views.assign',
            #         args=(self.centreid,'inputmod','simulation',s.id,))        
        
        if not fix and request.method=='POST':
            # we can't do the following, because on initialisation, we don't know what
            # s.id is for a new simulation
            #editURL=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,s.id))
            afterURL=reverse('cmip5q.protoq.views.simulationList',args=(self.centreid,))
            simform=SimulationForm(request.POST,instance=s)
            simform.specialise(self.centre)
            if simform.is_valid():
                if label=='Add':
                    oldmodel=None
                else: oldmodel=s.numericalModel
                news=simform.save()
                logging.debug('model before %s, after %s'%(oldmodel,news.numericalModel))
                if news.numericalModel!=oldmodel:news.resetConformances()
                return HttpResponseRedirect(afterURL)
            else:
                logging.debug('SIMFORM not valid [%s]'%simform.errors)
        else:
            simform=SimulationForm(instance=s)
            simform.specialise(self.centre)
        
        # work out what we want to say about couplings
        cset=[]
        if label !='Add': cset=s.numericalModel.couplings(s)
        for i in cset:
            i.valid=len(i.internalclosure_set.all())+len(i.externalclosure_set.all()) > 0 # need at least one closure
            
        # now work out what we want to say about conformances.
        cs=Conformance.objects.filter(simulation=s)
            
        return render_to_response('simulation.html',
            {'s':s,'simform':simform,'urls':urls,'label':label,'exp':e,
             'cset':cset,'coset':cs,'ensemble':ensemble,
             'tabs':tabs(request,self.centreid,'Simulation',s.id or 0)})
        
    def edit(self,request,fix=False):
        ''' Handle providing and receiving edit forms '''
       
        s=Simulation.objects.get(pk=self.simid)
        s.updateCoupling()
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
                self.url=reverse('cmip5q.protoq.views.viewExperiment',args=(c.id,id,))
                self.new=reverse('cmip5q.protoq.views.simulationAdd',args=(c.id,id,))
                
        csims=Simulation.objects.filter(centre=c)
        cpurl=reverse('cmip5q.protoq.views.simulationCopy',args=(c.id,))

        eset=Experiment.objects.all()
        for e in eset:
            sims=e.simulation_set.filter(centre=c.id)
            for s in sims: s.url=reverse('cmip5q.protoq.views.simulationEdit',args=(c.id,s.id,))    
            exp.append(etmp(e.shortName,sims,e.id))

        return render_to_response('simulationList.html',
            {'c':c,'experiments':exp,'csims':csims,'cpurl':cpurl,
            'tabs':tabs(request,c.id,'Experiments'),'notAjax':not request.is_ajax()})
 
    def conformanceMain(self,request):
        ''' Displays the main conformance view '''

        s=Simulation.objects.get(pk=self.simid)
        e=s.experiment
        
        urls={'self':reverse('cmip5q.protoq.views.conformanceMain',
                    args=(self.centreid,s.id,)),
              'mods':reverse('cmip5q.protoq.views.assign',
                    args=(self.centreid,'modelmod','simulation',s.id,)),
              'sim':reverse('cmip5q.protoq.views.simulationEdit',
                    args=(self.centreid,s.id,))
                    }
        #con=Conformance.objects.filter(simulation=s)
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
                    'urls':urls,'tabs':tabs(request,self.centreid,'Conformance')})
  
    def copy(self,request):
        if request.method=='POST':
                #try:
                if request.POST['targetSim']=='---':
                    return HttpResponse('Error, please choose a simulation to copy. You can use your browser back button')
                targetExp=request.POST['targetExp']
                exp=Experiment.objects.get(id=targetExp)
                targetSim=request.POST['targetSim']
                s=Simulation.objects.get(id=targetSim)
                ss=s.copy(exp)
                url=reverse('cmip5q.protoq.views.simulationEdit',args=(self.centreid,ss.id,))
                return HttpResponseRedirect(url)
                #except Exception,e:
                return HttpResponse('ERROR, %s, malformed POST to simulation copy'%e)
        else:
            return self.list(request)
    
                