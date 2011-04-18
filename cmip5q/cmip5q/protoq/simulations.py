# -*- coding: utf-8 -*-
# Create your views here.
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse

from cmip5q.protoq.models import *
from cmip5q.protoq.forms import *
from cmip5q.protoq.yuiTree import *
from cmip5q.protoq.layoutUtilities import tabs
from cmip5q.protoq.utilities import atomuri
from cmip5q.protoq.cimHandler import cimHandler, commonURLs

from django import forms
from django.conf import settings
logging=settings.LOG


ConformanceFormSet=modelformset_factory(Conformance,
                                        form=ConformanceForm,
                                        exclude=('simulation','requirement'))
                                        #exclude=('simulation'))

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
    ''' Simulation is an instance of a cim document which means there are some common methods '''
    
    def __init__(self,centre_id,simid=None,expid=None):
        ''' Initialise based on what the request needs '''
        self.centreid=centre_id
        self.centre=Centre.objects.get(pk=centre_id)
        self.pkid=simid
        self.expid=expid
        self.errors={}
        if self.pkid:
            self.s=Simulation.objects.get(pk=self.pkid)
            self.Klass=self.s.__class__
        else:
            self.s=None
            self.Klass='Unknown as yet by simulation handler'
        
    def __handle(self,request,s,e,url,label):
        ''' This method handles the form itself for both the add and edit methods '''
        logging.debug('entering simulation handle routine')
        
        if s.ensembleMembers>1:
            eset=s.ensemble_set.all()
            assert(len(eset)==1,'There can only be one ensemble set for %s'%s)
            members=eset[0].ensemblemember_set.all()
            ensemble={'set':eset[0],'members':members}
        else: ensemble=None
        
        #check that drsoutput info exists and if not create some
        x = s.drsOutput.all()
        if not x:
            s.updateDRS()
        
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
            urls['mod']=reverse('cmip5q.protoq.views.assign',
                     args=(self.centreid,'modelmod','simulation',s.id,))
            urls=commonURLs(s,urls)
            # dont think we should be able to get to input mods from here ...
            #urls['ics']=reverse('cmip5q.protoq.views.assign',
            #         args=(self.centreid,'inputmod','simulation',s.id,))        
        
        # A the moment we're only assuming one related simulation so we don't have to
        # deal with a formset
        rsims=s.related_from.all()
        if len(rsims):
            r=rsims[0]
        else: r=None
        if request.method=='POST':
            # do the simualation first ... 
            simform=SimulationForm(request.POST,instance=s,prefix='sim')
            simform.specialise(self.centre)
            if simform.is_valid():
                                 
                simok=True
                if label=='Add':
                    oldmodel=None
                    olddrs=None
                else: 
                    oldmodel=s.numericalModel
                    olddrs=s.drsMember
                    
                news=simform.save()
                logging.debug('model before %s, after %s'%(oldmodel,news.numericalModel))      
                
                if news.numericalModel!=oldmodel:
                    news.resetConformances()
                    news.resetCoupling()
                    
                if news.drsMember!=olddrs:
                    s.updateDRS()
                
            elif not simform.is_valid():
                simok=False
                logging.info('SIMFORM not valid [%s]'%simform.errors)
            relform=SimRelationshipForm(s,request.POST,instance=r,prefix='rel') 

            if relform.is_valid():
                if simok: 
                    r=relform.save()
                    return HttpResponseRedirect(news.edit_url())    
            else:
                # if there is no sto, then we should delete this relationship instance and move on.
                pass
            
            #generate a drs string instance in DRS Output class
            
            
        else:
            relform=SimRelationshipForm(s,instance=r,prefix='rel')
            simform=SimulationForm(instance=s,prefix='sim')
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
             'cset':cset,'coset':cs,'ensemble':ensemble,'rform':relform,
             'tabs':tabs(request,self.centreid,'Simulation',s.id or 0)})
            # note that cform points to simform too, to support completion.html
            
    def edit(self,request):
        ''' Handle providing and receiving edit forms '''
       
        s=self.s
        s.updateCoupling()
        
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
       
        u=atomuri()
        e=Experiment.objects.get(pk=self.expid)
        s=Simulation(uri=u,experiment=e,centre=self.centre)
        
        #grab the experiment duration if we can
        # there should be no more than one spatio temporal constraint, so let's get that one.
        
        stcg=e.requirements.filter(ctype__name='SpatioTemporalConstraint')
        if len(stcg)<>1:
            logging.info('Experiment %s has no duration (%s)?'%(e,len(stcg)))
        else:
            stc=stcg[0].get_child_object()
            print 'duration',stc.requiredDuration
            s.duration=stc.requiredDuration
        label='Add'
        
        return self.__handle(request,s,e,url,label)

    def list(self,request):
        ''' Return a listing of simulations for a given centre '''
        
        c=Centre.objects.get(pk=self.centreid)
       
        #little class to monkey patch up the stuff needed for the template
        class etmp:
            def __init__(self,abbrev,values,id):
                self.abbrev=abbrev
                self.values=values
                self.id=id
                self.url=reverse('cmip5q.protoq.views.viewExperiment',args=(c.id,id,))
                self.new=reverse('cmip5q.protoq.views.simulationAdd',args=(c.id,id,))
                
        csims=Simulation.objects.filter(centre=c).filter(isDeleted=False)
        cpurl=reverse('cmip5q.protoq.views.simulationCopy',args=(c.id,))

        eset=Experiment.objects.all()
        exp=[]
        for e in eset:
            sims=e.simulation_set.filter(centre=c.id).filter(isDeleted=False)
            for s in sims: s.url=reverse('cmip5q.protoq.views.simulationEdit',args=(c.id,s.id,))    
            exp.append(etmp(e.abbrev,sims,e.id))

        return render_to_response('simulationList.html',
            {'c':c,'experiments':exp,'csims':csims,'cpurl':cpurl,
            'tabs':tabs(request,c.id,'Experiments'),'notAjax':not request.is_ajax()})
 
    def conformanceMain(self,request):
        ''' Displays the main conformance view '''

        s=self.s
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
        else:
            return self.list(request)
        
    def resetCouplings(self):
        ''' This method completely resets ALL couplings and ALL closures from the 
        originals in the model. Note that copy does not do the closures, but
        this one does. One closure at a time can be done via the coupling handler. '''
        s=self.s
        s.resetCoupling(closures=True)
        # and return to the coupling view 
        url=reverse('cmip5q.protoq.views.simulationCup',
                    args=(self.centreid,s.id,))
        return HttpResponseRedirect(url)
                
