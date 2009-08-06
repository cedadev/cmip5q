from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from cmip5q.protoq.utilities import tabs
from django.http import HttpResponse,HttpResponseRedirect

class BaseViewHandler:
    ''' This is a base class to be used by the editors and listers
            '''
    def __init__(self,cen_id,resource,resourceType,form,editHTML,listHTML,selectHTML):
        ''' Pass the centre id (for access control), 
                resource model instance,
                resourceType string,
                the form CLASS for editing the resource,
                the template for editing an object, and
                the listing template. 
                 '''
        self.cid=cen_id
        self.resource=resource
        self.resourceType=resourceType
        self.resourceType4url=resourceType.lower()
        self.form=form
        self.editHTML=editHTML
        self.listHTML=listHTML
        self.selectHTML=selectHTML
         
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
                'form':self.form(),
                'editURL':editURL
                })
                
    def edit(self,request,object_id=None):
        ''' Edit/Update a specific object, or provide a form for a new object '''
        if object_id is None:
            editURL=reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url),)
            if request.method=='GET':
                #then we're starting afresh
                form=self.form()
            elif request.method=='POST':
                form=self.form(request.POST)
        else:
            editURL=reverse('cmip5q.protoq.views.edit',args=(self.cid,self.resourceType4url,object_id),)
            instance=self.resource.objects.get(id=object_id)
            if request.method=='GET':
                form=self.form(instance=instance)
            elif request.method=='POST':
                form=self.form(request.POST,instance=instance)
                    
        if request.method=='POST':
            if form.is_valid():
                f=form.save()
                return HttpResponseRedirect(
                          reverse('cmip5q.protoq.views.list',args=(self.cid,self.resourceType4url,)))
                          
        return render_to_response(self.editHTML,{'form':form,'editURL':editURL})
        
    def assign(self,request,target,targetURL):
        ''' This method binds to the target resource, a number of the resources managed
        by this one. eg If this class is instantiated with resourceType = file, and
        this method is called with an instance (target) of some class, then this
        method will bind the chosen files to that target, and then return to that
        target view via targetURL '''
         
        title='Assign %s(s) to %s'%(self.resourceType4url,target)
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
         
        if len(data)==0:
            return HttpResponseRedirect(reverse('cmip5q.protoq.views.list',
                                        args=(self.cid,self.resourceType4url,)))
        
        # We have two sorts of django attributes to deal with here,
        # foreign keys, and manytomany fields. 
        manager=target.__getattribute__(self.resourceType)
        
        # is it a manytomanyfield?
        many2many="<class 'django.db.models.fields.related.ManyRelatedManager'>"
        manyClass=str(type(manager))
        JustOne=(manyClass!=many2many)
        print many2many,manyClass,JustOne
        #need to get at the initial values and choose an appropriate form
        if JustOne:
            if manager is None: 
                initial=[]
            else: initial=[manager]
            ActualForm=AssignOneForm
        else:
            initial=manager.values()
            ActualForm=AssignForm
                          
        if request.method=='POST':
            rform=ActualForm(request.POST)
            if rform.is_valid():
                #now parse these up and assign to the resource
                if not JustOne:manager.clear()
                new=rform.cleaned_data['choose']
                if JustOne:
                    manager=objects.get(id=new)
                else:
                    for n in new:
                        r=objects.get(id=n)
                        manager.add(r)
                return HttpResponseRedirect(targetURL)
        elif request.method=='GET':
            #need to ensure that if there are none already chosen, we don't bind the form ...
            if len(initial)==0:
                rform=ActualForm()
            else:rform=ActualForm({'choose':initial})
                
        url=''#reverse('cmip5q.protoq.views.assignReferences',args=(self.cid,resourceType,resource_id,))
        return render_to_response(self.selectHTML,
            {'rform':rform,
                'title':title,
                'tabs':tabs(self.cid,'Chooser'),'url':url})
               
           
                
         
         