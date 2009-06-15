#
# Some code to support the navigation of model components 
#
from cmip5q.protoq.models import *
        
class ComponentFamily:
    ''' Used to provide a django template friendly structure for component heirarchy '''
    def __init__(self,component_id):
        ''' Initialise for a specific component '''
        me=Component.objects.get(pk=component_id)
        self.me=me.id
        self.ancestors=[]
        self.siblings=[]
        self.children=[m.id for m in me.components.all()]
        # Now build up a family tree
        self.__getFamily(me)
        
    def __getFamily(self,component):
        ''' Get my family tree '''
        parents=Component.objects.filter(components=component.id)
        if len(parents)==0: return 
        parent=parents[0]
        self.siblings=[i.id for i in parent.components.all()]
        self.siblings.remove(component.id)
        self.__getFogies(parent)
        
    def __getFogies(self,parent):
        ''' Get the parentage of the parents '''
        self.ancestors.insert(0,parent.id)
        parents=Component.objects.filter(components=parent.id)
        if len(parents)==0: return 
        parent=parents[0]
        self.__getFogies(parent)
        
class yuiTree:
    '''Provides an ordered list view of the component heirarchy as the .html attribute '''
    # Yes I know this breaks the nice django view of the world, but needs must.
    def __li(self,e,i,a):
        url=self.baseURL.replace('+EDID+','/%s/'%i)
        return '<li%s><a href="%s">%s</a>\n'%(e,url,a)
    def __init__(self,component,top='model',baseURL=''):
        self.baseURL=baseURL.replace('/%s/'%component,'+EDID+')
        string='<ul>\n'
        self.family=ComponentFamily(component)
        clist=Component.objects.filter(scienceType='model')
        for c in clist:
            cstring=''
            try:
                if c.id == self.family.ancestors[0]: cstring=' class="expanded"'
            except IndexError: pass
            string+=self.__li(cstring,c.id,c.abbrev)
            if cstring!='':
                string+='<ul>\n'
                #first just go down the parent tree opening stuff ...
                for cc in self.family.ancestors[1:]:
                    ccc=Component.objects.get(pk=cc)
                    string+=self.__li(cstring,ccc.id,ccc.abbrev)
                    string+='<ul>\n'
                ccc=Component.objects.get(pk=self.family.me)
                string+=self.__li(cstring,ccc.id,ccc.abbrev)
                string+='<ul>\n'
                #now sort out children
                for cc in self.family.children:
                    ccc=Component.objects.get(pk=cc)
                    string+=self.__li('',ccc.id,ccc.abbrev)+'</li>\n'
                string+='</ul></li>\n'
                #then siblings
                for cc in self.family.siblings:
                    ccc=Component.objects.get(pk=cc)
                    string+=self.__li('',ccc.id,ccc.abbrev)+'</li>\n'
                #now close all those back up to the ultimate parent.
                for cc in self.family.ancestors:
                    string+='</ul>'
            string+='</li>\n'
        string+='</ul>\n'
        self.html=string 
        
class yuiTree2:
    ''' Provides an ordered list view of the component heirarchy, for use
    by a yuiTree to control component visibility '''
    def __li(self,e,i,a,ok=0):
        url=self.baseURL.replace('+EDID+','/%s/'%i)
        ok1,ok2={0:('',''),1:('[',']')}[ok] #used to denote hanging chads (see debug)
        cc={1:' class="open"',0:''}[i==self.family.me]
        return '<li%s>%s<a href="%s"%s>%s</a>%s\n'%(e,ok1,url,cc,a,ok2)
    
    def __init__(self,component,top='model',baseURL=''):
        self.baseURL=baseURL.replace('/%s/'%component,'+EDID+')
        self.html='<ul>\n'
        self.found=[]
        self.family=ComponentFamily(component)
        self.expanders=self.family.ancestors
        self.expanders.append(self.family.me)
        clist=Component.objects.filter(scienceType='model')
        for c in clist: self.__walk(c)
        self.__debug()
        self.html+='</ul>\n'
    
    def __walk(self,component):
        ''' Show me and my children'''
        children=component.components.all()
        cstring=''
        if component.id in self.expanders: cstring=' class="expanded"'
       
        self.html+=self.__li(cstring,component.id,component.abbrev)
        self.found.append(component.id)
        if len(children)==0: return
        self.html+='<ul>\n'
        for c in children: self.__walk(c)
        self.html+='</ul>'
        
    def __debug(self):
        ''' Find the hanging chads, ie. the components that no longer have parents '''
        all=Component.objects.all()
        for a in all:
            found=(a.id in self.found)
            string='ok'
            if not found: 
                self.html+=self.__li(' class="bad"',a.id,a.abbrev,ok=1)+'</li>'
                p=Component.objects.filter(components=a.id)
                string=str(p)
            #print '%s(%s) shown in menu: %s (%s)(%s)'%(a.abbrev,a.id,found,a.scienceType,string)
            
                
        
                
      
    
    