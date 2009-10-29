from cmip5q.protoq.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from cmip5q.protoq.utilities import tabs
from django.http import HttpResponse,HttpResponseRedirect
from cmip5q.protoq.utilities import sublist
import logging

class BaseViewHandler:
    ''' This is a base class to be used by the editors and listers
            '''
    def __init__(self,centre_id,resource,target):
        ''' The base view handler is initialised with stuff that is known to the url mapping
        and exploits some knowledge of the specific resources. We shouldn't know anything
        about the specific resources in this class '''
                 
        self.cid=centre_id
        self.centre=Centre.objects.get(id=centre_id)
        self.resource=resource
        self.target=target
        
        self.editHTML='baseview_edit.html'#'%s_edit.html'%self.resource['type']
        self.listHTML='baseview_list.html'#'%s_list.html'%self.resource['type']
        self.selectHTML='baseviewAssign.html'
        
    def objects(self):
        ''' We use the superclass method '''
        return []
    
    def constraints(self):
        ''' We use the superclass method'''
        return None
    
    def _constructForm(self,method,*args,**kwargs):
        ''' Handle form construction '''
        if method == 'POST':
            return self.resource['form'](*args,**kwargs)
        elif method == 'GET':
            # FIXME we'll need to do the specialisation based on the 
            # target information ... postpone this again for now.
            form=self.resource['form'](*args,**kwargs)
            constraints=self.constraints()
            print 'constraints',constraints
            if constraints is not None: form.specialise(constraints)
            return form
        else:
            raise ValueError('Form construction only supports GET and POST')
                 
    def list(self,request):
        ''' Show a list of the basic entities, either all of them, or those
        associated with a specific instance of a specific class '''
        
        objects=self.objects()
        
        if self.target:

            # in the case of a list, the target is used to go back ...

            # get a URL for a blank form
            formURL=reverse('cmip5q.protoq.views.edit',
                            args=(self.cid,self.resource['type'],0,
                            self.target['type'],self.target['instance'].id,'list',))
            for o in objects:
                # monkey patch an edit URL into the object allowing for the target,
                # saying come back here (to the list). Unfortunately doing that
                # means we lose the incoming reference.
                args=(self.cid,self.resource['type'],o.id,
                                  self.target['type'],self.target['instance'].id,'list',)
                o.editURL=reverse('cmip5q.protoq.views.edit',args=args)
                o.delURL=reverse('cmip5q.protoq.views.delete',args=args)
                #o.delURL=reverse('cmip5q.protoq.views.delete',
                #            args=(self.cid,self.resource['type'],o.id,self.currentURL)
                # Need to be able to make sure this isn't an html get from an <a> otherwise
                # do it as  form with a method of delete.
        else:
            # get a URL for a blank form
            formURL=reverse('cmip5q.protoq.views.edit',
                            args=(self.cid,self.resource['type'],0,'list',))
            for o in objects:
                # monkey patch an edit URL into the object, saying come back here (list)
                args=(self.cid,self.resource['type'],o.id,'list',)
                o.editURL=reverse('cmip5q.protoq.views.edit',args=args)
                if o.centre==self.centre:
                    o.delURL=reverse('cmip5q.protoq.views.delete',args=args)
                else:
                    o.delURL=None
        # we pass a form and formURL for a new instance to be created.
        # we're doing all this because we think we have too many entities to use a formset
       
        return render_to_response(self.listHTML,{
                'objects':sublist(objects,3),
                'tabs':tabs(request,self.cid,self.resource['tab']),
                'form':self._constructForm('GET'),
                'editURL':formURL,
                'instance':self.resource,
                'snippet_template':'%s_snippet.html'%self.resource['type'],
                'target':self.target
                })
                
    def edit(self,request,returnType):
        ''' We normally see this method called as a GET when it's hyperlinked
        from a list or assign page, so we want to go back there in those cases.
        If it's a POST, then we handle it, and go back to the correct place,
        unless there is a problem. '''
            
        # The basic sequence when we receive an edit form as a post, is that 
        # if it's valid, return to where we came from. If it's not, we should show
        # a form, complete with errors, with a submission URL which gets the user
        # back to the right place.  A GET should set that process up.
        if self.target:
            okURL=reverse('cmip5q.protoq.views.%s'%returnType,
               args=(self.cid,self.resource['type'],self.target['type'],self.target['instance'].id,))
        else:
            okURL=reverse('cmip5q.protoq.views.%s'%returnType,
               args=(self.cid,self.resource['type'],))
        # Note that if the resource instance id is zero, this is a new one.
        instance=None
        if self.resource['id']<>'0':
            instance=self.resource['class'].objects.get(id=self.resource['id'])
                    
        if request.method=='POST':
            logging.debug('Handling post with %s, %s '%(self.resource,request.POST))
            form=self._constructForm('POST',request.POST,instance=instance)
            form.hostCentre=self.centre
            if form.is_valid():
                if returnType=='ajax': return HttpResponse('not implemented')
                logging.debug('Successful edit post, redirecting to %s'%okURL)
                form.save() ##################### WHY DID I JUST ADD THIS >>>> 23/9
                return HttpResponseRedirect(okURL)
            else:
                print 'ERRORS [%s]'%form.errors
                constraints=self.constraints()
                if constraints:form.specialise(constraints)
                
        if request.method=='GET':
            form=self._constructForm('GET',instance=instance)
        
        # Now construct a useful submission URL
        args=[self.cid,self.resource['type'],self.resource['id']]
        if self.target:args+=[self.target['type'],self.target['instance'].id]
        if returnType: args.append(returnType)
        editURL=reverse('cmip5q.protoq.views.edit',args=args)
                          
        return render_to_response(self.editHTML,{'form':form,'editURL':editURL,'okURL':okURL,
                                                 'tabs':tabs(request,self.cid,'Edit %s'%instance),
                                                 'snippet_template':'%s_snippet.html'%self.resource['type'],
                                                 'resource':self.resource})
                                                 
                                                 
    def delete(self,request,returnType):
        ''' Delete an item ... '''
        if self.target:
            okURL=reverse('cmip5q.protoq.views.%s'%returnType,
               args=(self.cid,self.resource['type'],self.target['type'],self.target['instance'].id,))
        else:
            okURL=reverse('cmip5q.protoq.views.%s'%returnType,
               args=(self.cid,self.resource['type'],))
        if request.method=='POST':
            if self.resource['id']<>'0':
                instance=self.resource['class'].objects.get(id=self.resource['id'])
                if instance.centre==self.centre: 
                    instance.delete()
                    return HttpResponseRedirect(okURL)
                else:
                    return HttpResponse("Invalid")
        #all other cases are invalid
        return HttpResponse('Invalid')
        
    def assign(self,request):
        ''' This method binds to the target resource, a number of the resources managed
        by this one. eg If this class is instantiated with resourceType = file, and
        this method is called with an instance (target) of some class, then this
        method will bind the chosen files to that target, and then return to that
        target view via targetURL. We provide targetType and targetID to allow 
        the construction of return URLs when we go to the editor ...'''
         
        title='Assign %s(s) to %s'%(self.resource['type'],self.target['instance'])
        objects=self.objects()

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
        target=self.target['instance'] 
        manager=target.__getattribute__(self.resource['attname'])
        
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
                    target.__setattr__(self.resource['attname'],objects.get(id=new))
                else:
                    for n in new:
                        r=objects.get(id=n)
                        manager.add(r)
                target.save()
                return HttpResponseRedirect(self.target['url'])
        elif request.method=='GET':
            #need to ensure that if there are none already chosen, we don't bind the form ...
            if initial==[]:
                rform=ActualForm()
            else:rform=ActualForm({'choose':initial})
                
        url=''
        
        #editURL and form used to add a new instance.
        editURL=reverse('cmip5q.protoq.views.edit',
            args=(self.cid,self.resource['type'],0,self.target['type'],self.target['instance'].id,'assign'))
        listURL=reverse('cmip5q.protoq.views.list',
            args=(self.cid,self.resource['type'],self.target['type'],self.target['instance'].id))
            
        return render_to_response(self.selectHTML,
            {'showChoices':showChoices,
                'rform':rform,
                'title':title,
                'form':self._constructForm('GET'),
                'editURL':editURL,'listURL':listURL,
                'editTemplate':'%s_snippet.html'%self.resource['type'],
                'tabs':tabs(request,self.cid,'Assign %s'%self.resource['type']),
                'chooseURL':url})
               
           
                
         
         