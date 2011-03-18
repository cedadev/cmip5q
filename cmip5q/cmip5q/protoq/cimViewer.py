from django.core.urlresolvers import reverse
import string


#namespaces used within the CIM
cimns = 'http://www.metaforclimate.eu/schema/cim/1.5'
gmdns = 'http://www.isotc211.org/2005/gmd'
gcons = 'http://www.isotc211.org/2005/gco'
xsins = 'http://www.w3.org/2001/XMLSchema-instance'



def modeliter(elemroot, modelhtml):
    
    # find and mark up main component information
    mihtml=[]
    mihtml.append('<li>')
    mihtml.append('<h5>Overview Information</h5>')
    mihtml.append('<div class="inner">')
    modshortname = elemroot.find('shortName')
    modlongname = elemroot.find('longName')
    moddescription = elemroot.find('description')
    modtype = elemroot.find('type').get('value')
    #first non-attribute information
    for mi in [modshortname,modlongname,moddescription]:
        if mi is not None:
            #tagminns = mi.tag.split(cimns + '}')[1]
            mihtml.append('            <table>')
            mihtml.append('                <tr height="5px">')
            mihtml.append('                    <td width = 20%>')
            mihtml.append('                        <p class="titletext">%s</p>' %mi.tag)
            mihtml.append('                    </td>')
            mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %mi.text)
            mihtml.append('                </tr> ')
            mihtml.append('            </table>')
    #and now attribute info
    if modtype is not None:
        mihtml.append('            <table>')
        mihtml.append('                <tr height="5px">')
        mihtml.append('                    <td width = 20%>')
        mihtml.append('                        <p class="titletext">type</p>')
        mihtml.append('                    </td>')
        mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %modtype)
        mihtml.append('                </tr> ')
        mihtml.append('            </table>')
    
    mihtml.append('</div>')
    mihtml.append('</li>')
    
    
    # find and mark up responsible party info
    respParties=elemroot.findall('{%s}responsibleParty' %cimns)
    rphtml=[]
    if respParties:
        rphtml.append('<li>')
        rphtml.append('<h5>Responsible Parties</h5>')
        rphtml.append('<div class="inner">')
        for party in respParties:
            rp_iter(party,rphtml)
        rphtml.append('</div>')
        rphtml.append('</li>')
        
        
    # find and mark up component properties 
    compProps = elemroot.findall('componentProperties/componentProperty' )
    cphtml=[]
    if compProps:   
        cphtml.append('<li>')
        cphtml.append('<h5>Component Properties</h5>')
        cphtml.append('<div class="inner">')
        for cp in compProps:
            cp_iter(cp,cphtml)
        cphtml.append('</div>')
        cphtml.append('</li>')
        
        
    # find and mark up document information
    dihtml=[]
    dihtml.append('<li>')
    dihtml.append('<h5>Document Information</h5>')
    dihtml.append('<div class="inner">')
    docid = elemroot.find('documentID')
    docversion = elemroot.find('documentVersion')
    docdate = elemroot.find('documentCreationDate')
    
    for di in [docid,docversion,docdate]:
        if di is not None:
            #tagminns = di.tag.split(cimns + '}')[1]
            dihtml.append('            <table>')
            dihtml.append('                <tr height="5px">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' %di.tag)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    dihtml.append('</div>')
    dihtml.append('</li>')
    
    
    # find and mark up child components
    childComponents=elemroot.findall('childComponent/modelComponent') 
    cchtml=[]
    if childComponents:   
        cchtml.append('<li>')
        cchtml.append('<h5>Child Components</h5>')
        cchtml.append('<div class="inner">')
        for cc in childComponents:
            modshortname = cc.find('shortName')
            cchtml.append('<li>')
            cchtml.append('<h5>%s</h5>' %modshortname.text)
            cchtml.append('<div class="inner">')
            modeliter(cc, cchtml)
            cchtml.append('</div>')
            cchtml.append('</li>')
        cchtml.append('</div>')
        cchtml.append('</li>')
   
   
    # consolidate required blocks of html    
    modelhtml += mihtml
    modelhtml += rphtml
    modelhtml += dihtml
    modelhtml += cphtml
    modelhtml += cchtml
    return modelhtml


def expiter(elemroot, exphtml):
    
    # find and mark up main experiment information
    mihtml=[]
    mihtml.append('<li>')
    mihtml.append('<h5>Overview Information</h5>')
    mihtml.append('<div class="inner">')
    expshortname = elemroot.find('{%s}shortName' %cimns)
    explongname = elemroot.find('{%s}longName' %cimns)
    expdescription = elemroot.find('{%s}description' %cimns)
    exprat = elemroot.find('{%s}rationale' %cimns)
    expstart = elemroot.find('{%s}requiredDuration/{%s}startDate' %(cimns,cimns))
    expend = elemroot.find('{%s}requiredDuration/{%s}endDate' %(cimns,cimns))
    #first non-attribute information
    for mi in [expshortname,explongname,expdescription,exprat,expstart,expend]:
        if mi is not None:
            tagminns = mi.tag.split(cimns + '}')[1]
            mihtml.append('            <table>')
            mihtml.append('                <tr height="5px">')
            mihtml.append('                    <td width = 20%>')
            mihtml.append('                        <p class="titletext">%s</p>' %tagminns)
            mihtml.append('                    </td>')
            mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %mi.text)
            mihtml.append('                </tr> ')
            mihtml.append('            </table>')
      
    mihtml.append('</div>')
    mihtml.append('</li>')
 
    
    # find and mark up numerical requirement info
    numReqs=elemroot.findall('{%s}numericalRequirement' %cimns)
    if numReqs:
        nrhtml=[]
        nrhtml.append('<li>')
        nrhtml.append('<h5>Numerical Requirements</h5>')
        nrhtml.append('<div class="inner">')
        nrhtml.append('            <table>')
        nrhtml.append('                <tr height="5px">')
        nrhtml.append('                    <td width = 20%>')
        nrhtml.append('                        <p class="titletext">Name</p>')
        nrhtml.append('                    </td>')
        nrhtml.append('                    <td width = 20%>')
        nrhtml.append('                        <p class="titletext">Type</p>')
        nrhtml.append('                    </td>')
        nrhtml.append('                    <td width = 60%>')
        nrhtml.append('                        <p class="titletext">Description</p>')
        nrhtml.append('                    </td>')
        nrhtml.append('                </tr> ')
        nrhtml.append('            </table>')
        nrhtml.append('            <hr/>')
        nrhtml.append('            <br/>')
        for nr in numReqs:
            nrname = nr.find('{%s}name' %cimns).text
            nrdescription = nr.find('{%s}description' %cimns).text
            nrtype = nr.get('{%s}type' %xsins)
            #nameminns = n.tag.split(cimns + '}')[1]
            nrhtml.append('            <table>')
            nrhtml.append('                <tr height="5px">')
            nrhtml.append('                    <td width = 20%>')
            nrhtml.append('                        <p class="bodytext">%s</p>' %nrname)
            nrhtml.append('                    </td>')
            nrhtml.append('                    <td width = 20%>')
            nrhtml.append('                        <p class="bodytext">%s</p>'  %nrtype)
            nrhtml.append('                    </td>')
            nrhtml.append('                    <td width = 60%>')
            nrhtml.append('                        <p class="bodytext">%s</p>'  %nrdescription)
            nrhtml.append('                    </td>')
            nrhtml.append('                </tr> ')
            nrhtml.append('            </table>')
            
         
        nrhtml.append('</div>')
        nrhtml.append('</li>')
    
    
    # find and mark up document information
    dihtml=[]
    dihtml.append('<li>')
    dihtml.append('<h5>Document Information</h5>')
    dihtml.append('<div class="inner">')
    docid = elemroot.find('{%s}documentID' %cimns)
    docversion = elemroot.find('{%s}documentVersion' %cimns)
    docdate = elemroot.find('{%s}documentCreationDate' %cimns)
    
    for di in [docid,docversion,docdate]:
        if di is not None:
            tagminns = di.tag.split(cimns + '}')[1]
            dihtml.append('            <table>')
            dihtml.append('                <tr height="5px">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' %tagminns)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    dihtml.append('</div>')
    dihtml.append('</li>')
    
    # consolidate required blocks of html    
    exphtml += mihtml
    exphtml += nrhtml
    exphtml += dihtml
    return exphtml



def rp_iter(elemroot, rphtml):
    cl=elemroot.find('role/CI_RoleCode')
    role=cl.get('codeListValue')
    #get individual name or organisation name
    if elemroot.findtext('individualName/CharacterString'):
        name=elemroot.findtext('individualName/CharacterString')
    else:
        name=elemroot.findtext('organisationName/CharacterString')
    address=elemroot.findtext('contactInfo/CI_Contact/address/CI_Address/deliveryPoint/CharacterString')
    email = elemroot.findtext('contactInfo/CI_Contact/address/CI_Address/electronicMailAddress/CharacterString')

    rphtml.append('            <table>')
    rphtml.append('                <tr height="5px">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">%s</p>' %role)
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')     
    rphtml.append('                      <p class="bodytext">%s'  %name)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('            </table>')
    
    return rphtml
    
    
def cp_iter(elemroot, cphtml):
    cpshortname = elemroot.find('shortName')
    cpvalues = elemroot.findall('value')
    cpprops = elemroot.findall('componentProperty')
    cphtml.append('            <table>')
    cphtml.append('                <tr height="5px">')
    cphtml.append('                    <td width = 30%>')
    cphtml.append('                        <p class="titletext">%s</p>' %cpshortname.text)
    cphtml.append('                    </td>')
    cphtml.append('                    <td>')
    cphtml.append('                        <table>')
    for value in cpvalues:
        cphtml.append('                        <tr height="5px">')
        cphtml.append('                            <td>')
        cphtml.append('                                <p class="bodytext">%s</p>' %value.text)
        cphtml.append('                            </td>')
        cphtml.append('                        </tr> ')
    cphtml.append('                        </table>')
    cphtml.append('                    </td>')
    cphtml.append('                </tr>')
    cphtml.append('            </table>')
    for cp in cpprops:
        cp_iter(cp,cphtml)
           
    return cphtml




class CIMDoc:
    def __init__(self, CIMfile, viewType=None):
        self.CIMfile = CIMfile
        self.viewType = viewType
        
        
class modelView(CIMDoc):
    def genhtml(self,treeroot):
        modshortname = treeroot.find('shortName')
        modelhtml=[]
        modelhtml.append('<div id="acc_wrapper">') 
        modelhtml.append('    <div id="content">')  
        modelhtml.append('        <div id="container">')
        modelhtml.append('            <div id="main">')
        modelhtml.append('            <p class="titletext">Model View(s)</p>')
        modelhtml.append('              <hr/>')
        modelhtml.append('<ul class="accordion" id="acc1">')
        modelhtml.append('<li>')
        modelhtml.append('<h4>%s</h4>' %modshortname.text)
        modelhtml.append('<div class="inner">')
        modelhtml.append('<ul>')
        
        modeliter(treeroot, modelhtml)
        
        modelhtml.append('</ul>')
        modelhtml.append('</div>')
        modelhtml.append('</li>')
        modelhtml.append('</ul>')
        modelhtml.append('</div>')            
        modelhtml.append('</div>')
        modelhtml.append('</div>')
        modelhtml.append('</div>')
        self.code="".join(modelhtml)               
    
    
    def getnavname(self, model):
        modnavname = model.find('shortName')
        if modnavname is not None:
            self.navname=modnavname.text  
            self.urlname=string.join(modnavname.text.split(),"").replace('.','_')   
            #self.url=reverse('CIMView.viewer.views.docsMenu', args=(self.viewType,self.urlname))
    
    
class expView(CIMDoc):
    def genhtml(self,treeroot):
        expshortname = treeroot.find('shortName')
        exphtml=[]
        exphtml.append('<div id="acc_wrapper">') 
        exphtml.append('    <div id="content">')  
        exphtml.append('        <div id="container">')
        exphtml.append('            <div id="main">')
        exphtml.append('            <p class="titletext">Experiment View(s)</p>')
        exphtml.append('              <hr/>')
        exphtml.append('<ul class="accordion" id="acc1">')
        exphtml.append('<li>')
        exphtml.append('<h4>%s</h4>' %expshortname.text)
        exphtml.append('<div class="inner">')
        exphtml.append('<ul>')
        
        expiter(treeroot, exphtml)
        
        exphtml.append('</ul>')
        exphtml.append('</div>')
        exphtml.append('</li>')
        exphtml.append('</ul>')
        exphtml.append('</div>')            
        exphtml.append('</div>')
        exphtml.append('</div>')
        exphtml.append('</div>')
        self.code="".join(exphtml)   
    
    def getnavname(self, exp):
        expnavname = exp.find('shortName')
        
        if expnavname is not None:
            self.navname=expnavname.text
            self.urlname=string.join(expnavname.text.split(),"").replace('.','_')  
            self.url=reverse('CIMView.viewer.views.docsMenu', args=(self.viewType,self.urlname) )
 
class simView(CIMDoc):
    
    def getnavname(self, exp):
        simnavname = exp.find('shortName')
        
        if simnavname is not None:
            self.navname=simnavname.text
            self.urlname=string.join(simnavname.text.split(),"").replace('.','_')  
            self.url=reverse('CIMView.viewer.views.docsMenu', args=(self.viewType,self.urlname) )
    
    def getinfo(self, qnSims):
        for sim in qnSims:
            simshortname = sim.findall('shortName')[0]
            if simshortname is not None:
                self.shortname=simshortname.text
            simlongname = sim.findall('longName')[0]
            if simlongname is not None:
                self.longname=simlongname.text
                
class dataView(CIMDoc):
    
    def getnavname(self, data):
        datanavname = data.find('storage/ipStorage/fileName')
        documentID = data.find('documentID')
        if datanavname is not None:
            self.navname=datanavname.text  
            self.documentID = documentID.text
            self.urlname=string.join(datanavname.text.split(),"").replace('.','_')
            self.url=reverse('CIMView.viewer.views.docsMenu', args=(self.viewType,self.urlname) )
    
    def getinfo(self, qnData):
        for data in qnData:
            datafilename = data.findall('storage/ipStorage/fileName')[0]
            if datafilename is not None:
                self.filename=datafilename.text
           
        
          
                    
        