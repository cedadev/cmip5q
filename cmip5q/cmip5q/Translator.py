
from protoq.models import *

from lxml import etree as ET
import uuid
import logging
import datetime


class Translator:

    ''' Translates a questionnaire Doc class (Simulation, Component or Platform) into a CIM document (as an lxml etree instance) '''

    CIM_NAMESPACE = "http://www.metaforclimate.eu/cim/1.3"
    SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_INSTANCE_NAMESPACE_BRACKETS = "{"+SCHEMA_INSTANCE_NAMESPACE+"}"
    CIM_URL = "cim.xsd"
    GMD_NAMESPACE = "http://www.isotc211.org/2005/gmd"
    GMD_NAMESPACE_BRACKETS="{"+GMD_NAMESPACE+"}"
    GCO_NAMESPACE = "http://www.isotc211.org/2005/gco"
    GCO_NAMESPACE_BRACKETS="{"+GCO_NAMESPACE+"}"
    NSMAP = {None  : CIM_NAMESPACE,             \
             "xsi" : SCHEMA_INSTANCE_NAMESPACE, \
             "gmd" : GMD_NAMESPACE,             \
             "gco" : GCO_NAMESPACE}

    def __init__(self):
        ''' Set any initial state '''
        self.recurse=True
        self.outputComposition=True

    def cimRoot(self):
        ''' return the top level cim document invarient structure '''
        root=ET.Element('CIMRecord', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        ET.SubElement(root,'id').text='[TBD1]'
        return root

    def q2cim(self,ref,docType):

        method_name = 'add' + str(docType)
        logging.debug("q2cim calling "+method_name)
        method = getattr(self, method_name)
        root=self.cimRoot()
        cimDoc=method(ref,root)
        return cimDoc
        
    def addEnsemble(self,ensembleClass,rootElement):

        if ensembleClass :
            ensembleElement=ET.SubElement(rootElement,'Q_Ensemble')
            ET.SubElement(ensembleElement,'Q_Description').text=ensembleClass.description
            etypeValueElement=ET.SubElement(ensembleElement,'Q_EtypeValue')
            self.addValue(ensembleClass.etype,etypeValueElement)

    def addSimulation(self,simClass,rootElement):
        
        simElement=ET.SubElement(rootElement,'Q_Simulation')
        #Simulation isa Doc
        self.addDoc(simClass,simElement)
        modelElement=ET.SubElement(simElement,'Q_NumericalModel')
        self.addComponent(simClass.numericalModel,modelElement)
        ET.SubElement(simElement,'Q_EnsembleCount').text=str(simClass.ensembleMembers)
        # add ensemble information from Ensemble class
        ensemblesElement=ET.SubElement(simElement,'Q_Ensembles')
        ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
        for ensembleClass in ensembleClassSet :
            self.addEnsemble(ensembleClass,ensemblesElement)
        self.addExperiment(simClass.experiment,simElement)
        self.addPlatform(simClass.platform,simElement)
        self.addCentre(simClass.centre,simElement)
        ET.SubElement(simElement,'Q_AuthorList').text=simClass.authorList
        modelModsElement=ET.SubElement(simElement,'Q_ModelMods')
        for modelModClass in simClass.modelMod.all():
            self.addModelMod(modelModClass,modelModsElement)
        inputModsElement=ET.SubElement(simElement,'Q_InputMods')
        for inputModClass in simClass.inputMod.all():
            self.addInputMod(inputModClass,inputModsElement)
        return rootElement

    def addModification(self,modClass,rootElement) :
        if modClass :
            modElement=ET.SubElement(rootElement,'Q_Modification')
            mtypeValueElement=ET.SubElement(modElement,'Q_MtypeValue')
            self.addValue(modClass.mtype,mtypeValueElement)
            ET.SubElement(modElement,'Q_Description').text=modClass.description

    def addModelMod(self,modelModClass,rootElement) :
        if modelModClass :
            modelModElement=ET.SubElement(rootElement,'Q_ModelMod')
            # ModelMod isa Modification
            self.addModification(modelModClass,modelModElement)
            if modelModClass.component :
                compElement=ET.SubElement(modelModElement,'Q_ComponentRef')
                ET.SubElement(compElement,'Q_ComponentName').text=modelModClass.component.abbrev

    def addInputMod(self,inputModClass,rootElement) :
        if inputModClass :
            inputModElement=ET.SubElement(rootElement,'Q_InputMod')
            # InputMod isa Modification
            self.addModification(inputModClass,inputModElement)
            ET.SubElement(inputModElement,'Q_Date').text=str(inputModClass.date)
            couplingsElement=ET.SubElement(inputModElement,'Q_Couplings')
            for couplingClass in inputModClass.inputs.all():
                self.addCouplingRef(couplingClass,couplingsElement)

    def addCouplingRef(self,couplingClass,rootElement):
        if couplingClass :
            couplingElement=ET.SubElement(rootElement,'Q_CouplingRef')
            couplingElement=ET.SubElement(couplingElement,'Q_InputAbbreviation').text=couplingClass.targetInput.abbrev
            couplingElement=ET.SubElement(couplingElement,'Q_InputDescription').text=couplingClass.targetInput.description

    def addCentre(self,centreClass,rootElement):
        if centreClass :
            centreElement=ET.SubElement(rootElement,'Q_Centre')
            #centreClass is a ResponsibleParty
            self.addResp(centreClass.party,centreElement,'centre')

    def addVocab(self,vocabClass,rootElement):
        if vocabClass :
            vocabElement=ET.SubElement(rootElement,'Q_Vocab')
            ET.SubElement(vocabElement,'Q_Name').text=vocabClass.name
            ET.SubElement(vocabElement,'Q_URI').text=vocabClass.uri
            ET.SubElement(vocabElement,'Q_Note').text=vocabClass.note
            ET.SubElement(vocabElement,'Q_Version').text=vocabClass.version

    def addValue(self,valueClass,valueElement):
        if valueClass :
            ET.SubElement(valueElement,'Q_Value').text=valueClass.value
            self.addVocab(valueClass.vocab,valueElement)
            ET.SubElement(valueElement,'Q_Definition').text=valueClass.definition
            ET.SubElement(valueElement,'Q_Version').text=valueClass.version

    def addRequirement(self,reqClass,rootElement):
        if reqClass :
            reqElement=ET.SubElement(rootElement,'Q_NumericalRequirement')
            ET.SubElement(reqElement,'Q_Description').text=reqClass.description
            ET.SubElement(reqElement,'Q_Name').text=reqClass.name
            valueElement=ET.SubElement(reqElement,'Q_CtypeValue')
            self.addValue(reqClass.ctype,valueElement)

    def addExperiment(self,expClass,rootElement):
        expElement=ET.SubElement(rootElement,'Q_Experiment')
        ET.SubElement(expElement,'Q_Rationale').text=expClass.rationale
        ET.SubElement(expElement,'Q_Why').text=expClass.why
        reqsElement=ET.SubElement(expElement,'Q_NumericalRequirements')
        for reqClass in expClass.requirements.all():
            self.addRequirement(reqClass,reqsElement)
        ET.SubElement(expElement,'Q_DocID').text=expClass.docID
        ET.SubElement(expElement,'Q_ShortName').text=expClass.shortName
        ET.SubElement(expElement,'Q_LongName').text=expClass.longName
        ET.SubElement(expElement,'Q_StartDate').text=expClass.startDate
        ET.SubElement(expElement,'Q_EndDate').text=expClass.endDate
        

    def setComponentOptions(self,recurse,composition):

        self.recurse=recurse
        self.outputComposition=composition
    
    def addComponent(self,compClass,rootElement):

        if compClass :
            self.addChildComponent(compClass,rootElement,1,self.recurse)
        return rootElement

    def addDoc(self,docClass,rootElement):

        if docClass :
            docElement=ET.SubElement(rootElement,'Q_Doc')
            ET.SubElement(docElement,'Q_Title').text=docClass.title
            ET.SubElement(docElement,'Q_Abbrev').text=docClass.abbrev
            self.addResp(docClass.author,docElement,'author')
            self.addResp(docClass.funder,docElement,'funder')
            self.addResp(docClass.contact,docElement,'contact')
            self.addResp(docClass.metadataMaintainer,docElement,'metadataMaintainer')
            ET.SubElement(docElement,'Q_Description').text=docClass.description
            ET.SubElement(docElement,'Q_URI').text=docClass.uri
            ET.SubElement(docElement,'Q_MetadataVersion').text=docClass.metadataVersion
            ET.SubElement(docElement,'Q_DocumentVersion').text=str(docClass.documentVersion)
            ET.SubElement(docElement,'Q_Created').text=str(docClass.created)
            ET.SubElement(docElement,'Q_Updated').text=str(docClass.updated)
        

    def addPlatform(self,platClass,rootElement):

        if platClass :
            platElement=ET.SubElement(rootElement,'Q_Platform')
            #Platform isa Doc
            self.addDoc(platClass,platElement)
            # add centre info ???
            ET.SubElement(platElement,'Q_Compiler').text=platClass.compiler
            ET.SubElement(platElement,'Q_Vendor').text=platClass.vendor
            ET.SubElement(platElement,'Q_CompilerVersion').text=platClass.compilerVersion
            ET.SubElement(platElement,'Q_MaxProcessors').text=platClass.maxProcessors
            ET.SubElement(platElement,'Q_CoresPerProcessor').text=platClass.coresPerProcessor
            ET.SubElement(platElement,'Q_OperatingSystem').text=platClass.operatingSystem
            hardwareElement=ET.SubElement(platElement,'Q_HardwareVal')
            self.addValue(platClass.hardware,hardwareElement)
            processorElement=ET.SubElement(platElement,'Q_ProcessorVal')
            self.addValue(platClass.processor,processorElement)
            interconnectElement=ET.SubElement(platElement,'Q_InterconnectVal')
            self.addValue(platClass.interconnect,interconnectElement)
        return rootElement

    def addChildComponent(self,c,root,nest,recurse=True):

      if c.implemented:
        if nest==1:
          # TBD documentVersion
          comp=ET.SubElement(root,'modelComponent',{'documentVersion': '-1', 'CIMVersion': '1.3'})
        else:
          comp=ET.SubElement(root,'modelComponent')
        #Component isa Doc
        self.addDoc(c,comp)
        if self.outputComposition:
            '''composition'''
            self.composition(c,comp)
        if recurse:
            '''childComponent'''
            for child in c.components.all():
              if child.implemented:
                comp2=ET.SubElement(comp,'childComponent')
                self.addChildComponent(child,comp2,nest+1)
        '''parentComponent'''
        '''deployment'''
        '''shortName'''
        ET.SubElement(comp,'shortName').text=c.abbrev
        '''longName'''
        ET.SubElement(comp,'longName').text=c.title
        '''description'''
        ET.SubElement(comp,'description').text=c.description
        '''license'''
        '''componentProperties'''
        componentProperties=ET.SubElement(comp,'componentProperties')
        pgset=ParamGroup.objects.filter(component=c)
        for pg in pgset:
            constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
            pset=NewParam.objects.filter(constraint=constraintSet[0])
            if len(pset)>0:
                componentProperty={}
                if pg.name=="Component Attributes":
                    componentProperty=componentProperties
                else:
                    componentProperty=ET.SubElement(componentProperties,'componentProperty',{'represented':str(c.implemented).lower()})
                    '''shortName'''
                ET.SubElement(componentProperty,'shortName').text=pg.name
                '''longName'''
                ET.SubElement(componentProperty,'longName').text=pg.name
                
                # the internal questionnaire representation is that all parameters
                # are contained in a constraint group
                for con in constraintSet:
                    pset=NewParam.objects.filter(constraint=con)
                    for p in pset:
                        property=ET.SubElement(componentProperty,'componentProperty',{'represented':str(c.implemented).lower()})
                        '''shortName'''
                        ET.SubElement(property,'shortName').text=p.name
                        '''longName'''
                        ET.SubElement(property,'longName').text=p.name
                        '''description'''
                        '''value'''
                    # extract all value elements (separated by "|"
                        for value in p.value.split('|'):
                            stripSpaceValue=value.strip()
                            if stripSpaceValue!='':
                                ET.SubElement(property,'value').text=stripSpaceValue
                    #ET.SubElement(property,'ptype').text=p.ptype
                    #ET.SubElement(property,'vocab').text=p.vocab
        '''numericalProperties'''
        ET.SubElement(comp,'numericalProperties')
        '''scientificProperties'''
        ET.SubElement(comp,'scientificProperties')
        '''grid'''
        '''responsibleParty'''
        comp.append(ET.Comment("format for responsible party's is not yet determined"))
        resps=ET.SubElement(comp,"Q_responsibleParties")

        self.addResp(c.author,resps,'author')
        self.addResp(c.funder,resps,'funder')
        self.addResp(c.contact,resps,'contact')
        '''fundingSource'''
        '''citation'''
        references=ET.SubElement(comp,'Q_references')
        for ref in c.references.all():
            reference=ET.SubElement(references,'Q_reference')
            ET.SubElement(reference,'Q_name').text=ref.name
            ET.SubElement(reference,'Q_citation').text=ref.citation
            ET.SubElement(reference,'Q_link').text=ref.link

        ''' RF associating genealogy with the component rather than the document '''
        if (nest<=2):
            genealogy=ET.SubElement(comp,'Q_genealogy')
            ET.SubElement(genealogy,'Q_yearReleased').text=str(c.yearReleased)
            ET.SubElement(genealogy,'Q_previousVersion').text=c.otherVersion
            ET.SubElement(genealogy,'Q_previousVersionImprovements').text=c.geneology


        '''activity'''
        '''type'''
        #comp.append(ET.Comment("value attribute in element type should have value "+c.scienceType+" but this fails the cim validation at the moment"))
        #ET.SubElement(comp,'type',{'value':'other'}) # c.scienceType
        ET.SubElement(comp,'type').text=c.scienceType
        '''component timestep info not explicitely supplied in questionnaire'''
        #if nest==2:
                #timing=ET.SubElement(comp,'timing',{'units':'units'})
                #ET.SubElement(timing,'rate').text='rate'
        if nest==1:
            '''documentID'''
            ET.SubElement(comp,'documentID').text=c.uri
            '''documentAuthor'''
            #ET.SubElement(comp,'documentAuthor').text=c.contact
            ET.SubElement(comp,'documentAuthor').text="Metafor Questionnaire"
            '''documentCreationDate'''
            #ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())
            ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
            '''documentGenealogy'''
            # component genealogy is provided in the questionnaire
            '''quality'''
            # no quality information in the questionnaire at the moment
          

      else:
        logging.debug("component "+c.abbrev+" has implemented set to false")
      return

    def addResp(self,respClass,rootElement,respType):
        if (respClass) :
            respElement=ET.SubElement(rootElement,"Q_responsibleParty",{'type':respType})
            ET.SubElement(respElement,"Q_name").text=respClass.name
            ET.SubElement(respElement,"Q_webpage").text=respClass.webpage
            ET.SubElement(respElement,"Q_abbrev").text=respClass.abbrev
            ET.SubElement(respElement,"Q_email").text=respClass.email
            ET.SubElement(respElement,"Q_address").text=respClass.address
            ET.SubElement(respElement,"Q_uri").text=respClass.uri
        #resp=ET.SubElement(comp,'responsibleParty') #type gmd:xxxx
        #ciresp=ET.SubElement(resp,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        #name=ET.SubElement(resp,'gmd:individualName')
        #ET.SubElement(name,'gco:CharacterString').text=c.contact
        #name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
        ###ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=c.contact
        # </gmd:individualName/>
        # <gmd:organisationName/>
        # <gmd:positionName/>
        # <gmd:contactInfo>
        #contact=ET.SubElement(ciresp,'gmd:contactInfo')
        #contact=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'contactInfo')
        #cicontact=ET.SubElement(contact,self.GMD_NAMESPACE_BRACKETS+'CI_Contact')
        #     <gmd:phone/>
        #     <gmd:address>
        #address=ET.SubElement(cicontact,'gmd:address')
        #address=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'address')
        #ciaddress=ET.SubElement(address,self.GMD_NAMESPACE_BRACKETS+'CI_Address')
        #         <gmd:deliveryPoint/>
        #         <gmd:city/>
        #         <gmd:administrativeArea/>
        #         <gmd:postalCode/>
        #         <gmd:country/>
        #         <gmd:electronicMailAddress>
        #email=ET.SubElement(ciaddress,'gmd:electronicMailAddress')
        #ET.SubElement(email,'gco:CharacterString').text=c.email
        #email=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'electronicMailAddress')
        ###ET.SubElement(email,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=c.email
        #         </gmd:electronicMailAddress>
        #     </gmd:address>
        #     <gmd:onlineResource/>
        #     <gmd:hoursOfService/>
        #     <gmd:contactInstructions/>
        # </gmd:contactInfo>
        # <gmd:roll/>
        #role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')#empty

    def composition(self,c,comp):
        couplings=[]
        # couplings are all at the esm (root component) level
        if c.isModel:couplings=c.couplings()
        if len(couplings)>0:
            composition=ET.SubElement(comp,'composition')
            for coupling in couplings:
                connection=ET.SubElement(composition,'coupling')
                ET.SubElement(connection,'Q_sourceComponent').text=c.abbrev
                ET.SubElement(connection,'Q_sourceComponent').text=coupling.parent.component.abbrev
                ET.SubElement(connection,'Q_inputType').text=coupling.targetInput.ctype.value
                ET.SubElement(connection,'Q_inputAbbrev').text=coupling.targetInput.abbrev
                ET.SubElement(connection,'Q_inputDescrip').text=coupling.targetInput.description
                if coupling.targetInput.ctype.value=='BoundaryCondition':
                    if (coupling.ctype):
                        ET.SubElement(connection,'Q_type').text=coupling.ctype.value
                    else:
                        ET.SubElement(connection,'Q_type')
                    if (coupling.FreqUnits):
                        ET.SubElement(connection,'Q_freqUnits').text=coupling.FreqUnits.value
                    else:
                        ET.SubElement(connection,'Q_freqUnits')
                    ET.SubElement(connection,'Q_frequency').text=str(coupling.couplingFreq)
                    ET.SubElement(connection,'Q_manipulation').text=coupling.manipulation
                iClosures=InternalClosure.objects.filter(coupling=coupling)
                if len(iClosures)>0:
                    closures=ET.SubElement(connection,'Q_internalClosures')
                    for iclos in iClosures:
                        closure=ET.SubElement(closures,'Q_closure')
                        ET.SubElement(closure,'Q_spatialRegridding').text=iclos.spatialRegridding.value
                        ET.SubElement(closure,'Q_spatialType').text=iclos.spatialType.value
                        ET.SubElement(closure,'Q_temporalRegridding').text=iclos.temporalRegridding.value
                        ET.SubElement(closure,'Q_inputDescription').text=iclos.inputDescription
                        ET.SubElement(closure,'Q_target').text=iclos.target.abbrev
                eClosures=ExternalClosure.objects.filter(coupling=coupling)
                if len(eClosures)>0:
                    closures=ET.SubElement(connection,'Q_externalClosures')
                    for eclos in eClosures:
                        closure=ET.SubElement(closures,'Q_closure')
                        ET.SubElement(closure,'Q_spatialRegridding').text=eclos.spatialRegridding.value
                        ET.SubElement(closure,'Q_spatialType').text=eclos.spatialType.value
                        ET.SubElement(closure,'Q_temporalRegridding').text=eclos.temporalRegridding.value
                        ET.SubElement(closure,'Q_inputDescription').text=eclos.inputDescription
                        ET.SubElement(closure,'Q_target').text=eclos.target.variable
                #coupling=ET.SubElement(composition,'coupling')
                #ET.SubElement(composition,'description').text='Composition information associated with component '+c.abbrev
                '''connection'''
                '''description'''
                '''timeProfile'''
                '''timeLag'''
                '''spatialRegridding'''
                '''timeTransformation'''
                '''couplingSource'''
                #source=ET.SubElement(coupling,'couplingSource',{'purpose':'xxx','fullySpecified':'????'})
                #sourceRef=ET.SubElement(source,'reference',{'xlinkXXXhref':'AddLocationHere'})
                '''couplingTarget'''
                '''priming'''

