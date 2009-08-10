from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from cmip5q.protoq.utilities import tabs
from django.http import HttpResponse,HttpResponseRedirect
import logging

class BaseViewHandler:
    ''' This is a base class to be used by the editors and listers
            '''
    def __init__(self,data):
        ''' The base view handler is initialised with stuff that is known to the url mapping
        and exploits some knowledge of the specific resources. We shouldn't know anything
        about the specific resources in this class '''
                 
        self.cid=data['centre']
        self.resource=data['resource']['class']
        self.resourceType=data['resource']['type']
        self.resourceType4url=self.resourceType.lower()
        self.resourceID=data['resource']['id']
        self.form=data['form']
        self.editHTML='%s_edit.html'%self.resourceType
        self.listHTML='%s_list.html'%self.resourceType
        self.selectHTML='baseviewAssign.html'
        # the following is a tuple of constraints which go into the form constructor
        self.constraints=data['constraints']
        self.target=data['target']['instance']
        self.targetID=data['target']['id']
        self.targetURL=data['target']['url']
        self.targetType=data['target']['type']
        
        logging.debug('BaseViewHandler initialised with %s'%data)
        
    def _constructForm(self,method,*args,**kwargs):
        ''' Handle form construction '''
        if method == 'POST':
            return self.form(*args,**kwargs)
        elif method == 'GET':
            if self.constraints:
                form=self.form(*args,**kwargs)
                form.specialise(*self.constraints)
                return form
            else: return self.form(*args,**kwargs)
        else:
            raise ValueError('Form construction only supports GET and POST')
                 
    def list(self):
        ''' Show a list of the basic entities '''
        objects=self.resource.objects.all()
        for o in objects:
            o.editURL= reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url,o.id),)
        c=Centre.objects.get(id=self.cid)
        editURL=reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url),)
        return render_to_response(self.listHTML,{
                'objects':objects,
                'tabs':tabs(self.cid,self.resourceType),
                'form':self._constructForm('GET'),
                'editURL':editURL
                })
                
    def edit(self,request):
        ''' Edit/Update a specific object, or provide a form for a new object '''
        if self.resourceID is None:
            #editURL=reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url,))
            editURL=reverse('cmip5q.protoq.views.edit',
                   args=(self.cid,self.resourceType4url,self.targetType,self.targetID))
            if request.method=='GET':
                #then we're starting afresh
                form=self._constructForm('GET')
            elif request.method=='POST':
                form=self._constructForm('POST',request.POST)
        else:
            editURL=reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url,self.resrourceID,self.targetType,self.targetID,),)
            instance=self.resource.objects.get(id=self.resurceID)
            if request.method=='GET':
                form=self._constructForm('GET',instance=instance)
            elif request.method=='POST':
                form=self._constructForm('POST',request.POST,instance=instance)
                    
        if request.method=='POST':
            if form.is_valid():
                f=form.save()
                if self.targetType is not None:
                    url=reverse('cmip5q.protoq.views.assign',
                            args=(self.cid,self.targetType,self.targetID,self.resourceType4url,))
                else:
                    url=reverse('cmip5q.protoq.views.list',
                            args=(self.cid,self.resourceType4url,))
                logging.debug('Successful edit post, redirecting to %s'%url)
                return HttpResponseRedirect(url)
            else:
                if self.constraints: form.specialise(*self.constraints)
                          
        return render_to_response(self.editHTML,{'form':form,'editURL':editURL})
        
    def assign(self,request):
        ''' This method binds to the target resource, a number of the resources managed
        by this one. eg If this class is instantiated with resourceType = file, and
        this method is called with an instance (target) of some class, then this
        method will bind the chosen files to that target, and then return to that
        target view via targetURL. We provide targetType and targetID to allow 
        the construction of return URLs when we go to the editor ...'''
         
        title='Assign %s(s) to %s'%(self.resourceType4url,self.target)
        objects=self.resource.objects.all()
        data=[(r.id,str(r)) for r in objects]
        
        # two possible forms could be used, multiple choice, or single choice.
        class AssignForm(forms.Form):
            ''' Used for producing a form for selection of multiple choices '''
            choose=forms.MultipleChoiceField(choices=data,
                          widget=forms.CheckboxSelectMultiple())
        class AssignOneForm(forms.Form):
            ''' Used for selecting just one option from a list '''
            choose=forms.ChoiceField(choices=data)
         
        showChoices=len(data)
        
        # We have two sorts of django attributes to deal with here,
        # foreign keys, and manytomany fields. 
        manager=self.target.__getattribute__(self.resourceType)
        
        # is it a manytomanyfield?
        many2many="<class 'django.db.models.fields.related.ManyRelatedManager'>"
        manyClass=str(type(manager))
        JustOne=(manyClass!=many2many)
        #need to get at the initial values and choose an appropriate form
        if JustOne:
            if manager is None: 
                initial=[]
            else: initial=manager.id
            ActualForm=AssignOneForm
        else:
            initial=[i.id for i in manager.get_query_set()]
            ActualForm=AssignForm
                          
        if request.method=='POST':
            rform=ActualForm(request.POST)
            if rform.is_valid():
                #now parse these up and assign to the resource
                if not JustOne:manager.clear()
                new=rform.cleaned_data['choose']
                if JustOne:
                    self.target.__setattr__(self.resourceType,objects.get(id=new))
                    print 'Assigned?',self.target.__getattribute__(self.resourceType)
                else:
                    for n in new:
                        r=objects.get(id=n)
                        manager.add(r)
                self.target.save()
                print self.target.initialCondition
                return HttpResponseRedirect(self.targetURL)
        elif request.method=='GET':
            #need to ensure that if there are none already chosen, we don't bind the form ...
            print 'initial',initial
            if initial==[]:
                rform=ActualForm()
            else:rform=ActualForm({'choose':initial})
                
        url=''#reverse('cmip5q.protoq.views.assignReferences',args=(self.cid,resourceType,resource_id,))
        editURL=reverse('cmip5q.protoq.views.edit',
            args=(self.cid,self.resourceType4url,self.targetType,self.targetID))
        return render_to_response(self.selectHTML,
            {'showChoices':showChoices,
                'rform':rform,
                'title':title,
                'form':self._constructForm('GET'),
                'editURL':editURL,
                'editTemplate':'%s_snippet.html'%self.resourceType,
                'tabs':tabs(self.cid,'Chooser'),
                'chooseURL':url})
               
           
                
         
         