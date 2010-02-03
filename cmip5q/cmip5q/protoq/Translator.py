
from protoq.models import *

from lxml import etree as ET
import uuid
import logging
import datetime


class Translator:


    ''' Translates a questionnaire Doc class (Simulation, Component or Platform) into a CIM document (as an lxml etree instance) '''

    # we can switch between the old xml simulation output provided in beta2 (CIMXML=False) and the new (more) CIM compliant simulation (CIMXML=True) with the following variable
    CIMXML=True
    # only valid CIM will be output if the following is set to true. This means that all information will not be output
    VALIDCIMONLY=True

    CIM_NAMESPACE = "http://www.metaforclimate.eu/cim/1.4"
    SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_INSTANCE_NAMESPACE_BRACKETS = "{"+SCHEMA_INSTANCE_NAMESPACE+"}"
    CIM_URL = "cim.xsd"
    GMD_NAMESPACE = "http://www.isotc211.org/2005/gmd"
    GMD_NAMESPACE_BRACKETS="{"+GMD_NAMESPACE+"}"
    GCO_NAMESPACE = "http://www.isotc211.org/2005/gco"
    GCO_NAMESPACE_BRACKETS="{"+GCO_NAMESPACE+"}"
    XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
    XLINK_NAMESPACE_BRACKETS="{"+XLINK_NAMESPACE+"}"
    NSMAP = {None    : CIM_NAMESPACE,             \
             "xsi"   : SCHEMA_INSTANCE_NAMESPACE, \
             "gmd"   : GMD_NAMESPACE,             \
             "gco"   : GCO_NAMESPACE,             \
             "xlink" : XLINK_NAMESPACE}

    def __init__(self):
        ''' Set any initial state '''
        self.recurse=True
        self.outputComposition=False # aka coupling information
        self.simClass=None

    def c2text(self,c):
        comp=ET.Element('div')
        
        ET.SubElement(comp,'h1').text='Component details'

        # component location in the hierarchy
        tmpComp=c
        compHierarchy=''
        while not tmpComp.isModel :
            parents=Component.objects.filter(components=tmpComp)
            assert len(parents)==1 ,'I am expecting one and only one parent'
            tmpComp=parents[0]
            compHierarchy='/'+tmpComp.abbrev+compHierarchy
        ET.SubElement(comp,'p').text='Location : '+compHierarchy
            
        '''shortName'''
        ET.SubElement(comp,'p').text='Short Name : '+c.abbrev
        '''longName'''
        ET.SubElement(comp,'p').text='Long Name : '+c.title
        '''description'''
        ET.SubElement(comp,'p').text='Description : '+c.description

        # add any references
        ET.SubElement(comp,'h1').text='References ['+str(len(c.references.all()))+']'
        for reference in c.references.all():
            #ET.SubElement(comp,'p').text='name: '+reference.name
            ET.SubElement(comp,'p').text=reference.citation
            #ET.SubElement(comp,'p').text='link: '+reference.link
            #if reference.refType :
            #    ET.SubElement(comp,'p').text='type: '+reference.refType.value

        ET.SubElement(comp,'h1').text='Properties'
        
        table=ET.SubElement(comp,'table',{'border':'1'})
        titleRow=ET.SubElement(table,'tr')
        ET.SubElement(titleRow,'td').text='Property'
        ET.SubElement(titleRow,'td').text='Definition'
        ET.SubElement(titleRow,'td').text='Type'
        ET.SubElement(titleRow,'td').text='Options'
        ET.SubElement(titleRow,'td').text='Value'

        pgset=ParamGroup.objects.filter(component=c)
        for pg in pgset:
            constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
            pset=NewParam.objects.filter(constraint=constraintSet[0])
            if len(pset)>0:
                '''name'''
                # ET.SubElement(comp,'p').text='name (pg) : '+pg.name
                # the internal questionnaire representation is that all parameters
                # are contained in a constraint group
                for con in constraintSet:
                    # we want to always output options with contraints in case people change their minds
                    # if self.constraintValid(con,constraintSet) :
                    if True :
                        pset=NewParam.objects.filter(constraint=con)
                        for p in pset:
                            row=ET.SubElement(table,'tr')
                            if con.constraint!='' :
                                ET.SubElement(row,'td').text=pg.name+':['+con.constraint+']'+p.name
                            else :
                                ET.SubElement(row,'td').text=pg.name+':'+p.name
                            '''definition'''
                            ET.SubElement(row,'td').text=p.definition
                            '''controlled vocab does not work as expected '''
                            # ET.SubElement(comp,'p').text='Controlled Vocabulary : '+str(p.controlled)
                            '''value'''
                            if p.ptype=='XOR' :
                                ET.SubElement(row,'td').text='One value from list'
                            elif p.ptype=='OR' :
                                ET.SubElement(row,'td').text='One or more values from list'
                            else :
                                myUnits=""
                                if p.units :
                                    myUnits=p.units
                                ValueType=""
                                if p.numeric :
                                    ValueType="numeric"
                                else :
                                    ValueType="string"
                                myType=""
                                ET.SubElement(row,'td').text='Unrestricted (units="'+myUnits+'") (type="'+ValueType+'")'

                            if p.vocab :
                                ''' I am constrained by vocab '''
                                ''' find all values associated with this vocab '''
                                # all values that are part of this vocab
                                valset=Value.objects.filter(vocab=p.vocab)
                                values=""
                                counter=0
                                for v in valset:
                                    '''name'''
                                    counter+=1
                                    values=values+v.value
                                    if counter != len(valset) :
                                        values=values+", "
                                ET.SubElement(row,'td').text=values
                            else :
                                ET.SubElement(row,'td').text='n/a'
                            ET.SubElement(row,'td').text=p.value
        return comp

    def cimRecord(self,rootElement,rootClass) :
        ''' return the top level cim document invarient structure '''
        cr1=ET.SubElement(rootElement,'CIMRecord')
        cr2=ET.SubElement(cr1,'CIMRecord')
        try :
            ET.SubElement(cr2,'id').text=rootClass.uri
            ET.SubElement(cr2,'version').text=str(rootClass.documentVersion)
        except :
            cr2.append(ET.Comment('ID TBD for '+rootClass._meta.module_name))
            ET.SubElement(cr2,'id').text='00000000-0000-0000-0000-000000000000'
            ET.SubElement(cr2,'version').text='0'
        return cr2
    
    def cimRecordRoot(self,rootClass):
        ''' return the top level cim document invarient structure '''
        root=ET.Element('CIMRecord', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        ET.SubElement(root,'id').text=rootClass.uri
        ET.SubElement(root,'version').text=str(rootClass.documentVersion)
        return root

    def cimRecordSetRoot(self):
        ''' return the top level cim document invarient structure '''
        root=ET.Element('CIMRecordSet', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        # generate a uuid on the fly for a recordset.
        ET.SubElement(root,'id').text=str(uuid.uuid1())
        ET.SubElement(root,'version').text='1'
        return root

    def q2cim(self,ref,docType):

        ''' primary public entry point. '''
        method_name = 'add_' + str(docType)
        logging.debug("q2cim calling "+method_name)
        method = getattr(self, method_name)
        # make a special case for simulation as we output
        # all information associated with a simulation
        # using a CIMRecordSet
        if method_name=='add_simulation' and self.CIMXML :
            root=self.cimRecordSetRoot()
            modelElement=self.cimRecord(root,ref.numericalModel)
            self.add_component(ref.numericalModel,modelElement)
            simulationElement=self.cimRecord(root,ref)
            self.add_simulation(ref,simulationElement)
            experimentElement=self.cimRecord(root,ref.experiment)
            self.add_experiment(ref.experiment,experimentElement)
            platformElement=self.cimRecord(root,ref.platform)
            self.add_platform(ref.platform,platformElement)

            uniqueFileList=[]
            couplings=ref.numericalModel.couplings(simulation=self.simClass)
            for coupling in couplings :
                externalClosures=ExternalClosure.objects.filter(coupling=coupling)
                for externalClosure in externalClosures :
                    if externalClosure.targetFile not in uniqueFileList :
                        uniqueFileList.append(externalClosure.targetFile)
            for fileObject in uniqueFileList :
                dataObjectElement=self.cimRecord(root,fileObject)
                self.add_dataobject(fileObject,dataObjectElement)
            cimDoc=root
        else :
            root=self.cimRecordRoot(ref)
            cimDoc=method(ref,root)
        return cimDoc
        
    def addEnsemble(self,ensembleClass,rootElement):

        if ensembleClass :
            ensembleElement=ET.SubElement(rootElement,'Q_Ensemble')
            ET.SubElement(ensembleElement,'Q_Description').text=ensembleClass.description
            etypeValueElement=ET.SubElement(ensembleElement,'Q_EtypeValue')
            self.addValue(ensembleClass.etype,etypeValueElement)
            ensMembersElement=ET.SubElement(ensembleElement,'Q_EnsembleMembers')
            ensMemberClassSet=EnsembleMember.objects.filter(ensemble=ensembleClass)
            for ensMemberClass in ensMemberClassSet :
                self.addEnsMember(ensMemberClass,ensMembersElement)

    def addEnsMember(self,ensMemberClass,rootElement):

        if ensMemberClass :
            ensMemberElement=ET.SubElement(rootElement,'Q_EnsembleMember')
            ET.SubElement(ensMemberElement,'Q_Number').text=str(ensMemberClass.memberNumber)
            # reference the modification here to avoid replication as it is stored as part of the simulation
            self.addModificationRef(ensMemberClass.mod,ensMemberElement)

    def add_simulation(self,simClass,rootElement):

        if (self.CIMXML):
            #single simulation
            simElement=ET.SubElement(rootElement,'simulationRun',{'CIMVersion':'1.4'})
            ''' responsibleParty [0..inf] '''
            self.addResp(simClass.contact,simElement,'contact')
            self.addResp(simClass.author,simElement,'author')
            self.addResp(simClass.funder,simElement,'funder')
            self.addResp(simClass.centre.party,simElement,'centre')
            ''' principleInvestigator [0..inf] '''
            ''' fundingSource [0..inf] '''
            ''' rationale [1..inf] '''
            ET.SubElement(simElement,'rationale').text=simClass.description
            ''' supports [1..inf] '''
            experimentElement=ET.SubElement(simElement,'supports')
            self.addCIMReference(simClass.experiment,experimentElement)
            ''' shortName [1] '''
            ET.SubElement(simElement,'shortName').text=simClass.abbrev
            ''' longName [1] '''
            ET.SubElement(simElement,'longName').text=simClass.title
            ''' description [0..1] '''
            ''' dataholder [0..inf] '''
            ''' conformance [0..inf] '''
            confClassSet=Conformance.objects.filter(simulation=simClass)
            for confClass in confClassSet:
                if (confClass.ctype) : # I have a conformance specified
                    if confClass.ctype.value=='Not Conformant' :
                        confElement=ET.SubElement(simElement,'conformance',{'conformant':'false'})
                    else :
                        confElement=ET.SubElement(simElement,'conformance',{'conformant':'true'})
                    confElement.append(ET.Comment("Conformance type "+confClass.ctype.value))
                    reqElement=ET.SubElement(confElement,'requirement')
                    deployReference=ET.SubElement(reqElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':''}) # a blank href means the same document
                    assert(confClass.requirement)
                    ET.SubElement(deployReference,'id').text=confClass.requirement.name
                    #ET.SubElement(deployReference,'name').text=
                    #ET.SubElement(deployReference,'version').text=
                    ET.SubElement(deployReference,'description').text='The numerical requirement to which this conformance relates. This numerical requirement is specified in the experiment to which the simulation that contains this conformance relates.'
                    # for each modelmod modification
                    for modClass in confClass.mod.all():
                        sourceElement=ET.SubElement(confElement,'source')
                        sourceReference=ET.SubElement(sourceElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':''}) # a blank href means the same document
                        im=None
                        mm=None
                        try:
                            im=modClass.inputmod
                        except:
                            mm=modClass.modelmod
                        if im:
                            ET.SubElement(sourceReference,'id').text='TBD'
                        elif mm:
                            ET.SubElement(sourceReference,'id').text=modClass.modelmod.component.uri
                        else:
                            assert(False) # error
                        #ET.SubElement(courceReference,'name').text=
                        #ET.SubElement(sourceReference,'version').text=
                        assert(modClass.mtype)
                        ET.SubElement(sourceReference,'description').text=modClass.description
                        sourceReference.append(ET.Comment('source reference mnemonic :: '+modClass.mnemonic))
                        sourceReference.append(ET.Comment('source reference type :: '+modClass.mtype.value))

                    # for each modelmod modification
                    for couplingClass in confClass.coupling.all():
                        sourceElement=ET.SubElement(confElement,'source')
                        assert couplingClass.targetInput, 'Error, couplingclass should have a targetinput'
                        targetInput=couplingClass.targetInput
                        sourceReference=ET.SubElement(sourceElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':'#'+targetInput.abbrev}) # a blank href means the same document

                    ET.SubElement(confElement,'description').text=confClass.description

            ''' simulationComposite [0..1] '''
            ''' ensemble [0..1] '''
            if (simClass.ensembleMembers>1 and not(self.VALIDCIMONLY)) :
                ensemblesElement=ET.SubElement(simElement,'Q_Ensembles')
                ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
                assert(len(ensembleClassSet)==1,'Simulation %s should have one and only one associated ensembles class'%simClass)
                for ensembleClass in ensembleClassSet :
                    self.addEnsemble(ensembleClass,ensemblesElement)
            ''' deployment [0..1] '''
            deployElement=ET.SubElement(simElement,'deployment')
            deployReference=ET.SubElement(deployElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':''}) # a blank href means the same document
            ET.SubElement(deployReference,'id').text=simClass.platform.uri
            #ET.SubElement(deployReference,'name').text=
            #ET.SubElement(deployReference,'version').text=
            ET.SubElement(deployReference,'description').text='The resources(deployment) on which this simulation ran'
            ''' input [0..inf] ???COUPLING??? '''
            ''' Duration [1] '''
            durationElement=ET.SubElement(simElement,'Duration')
            ''' duration element has an optional start date and an option end date '''
            ''' output [0..inf] '''
            ''' restart [0..inf] '''
            ''' spinup [0..1] '''
            ''' previousSimulation [0..1] '''
            ''' simulationID [0..1] '''
            ''' model [1] '''
            modelElement=ET.SubElement(simElement,'model')
            modelReference=ET.SubElement(modelElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':''}) # a blank href means the same document
            ET.SubElement(modelReference,'id').text=simClass.numericalModel.uri
            #ET.SubElement(modelReference,'name').text=
            #ET.SubElement(modelReference,'version').text=
            ET.SubElement(modelReference,'description').text='The numerical model which this simulation used'
            ''' startPoint [1] '''
            startElement=ET.SubElement(simElement,'startPoint')
            ''' startPoint element has an optional start date and an option end date '''
            ''' endPoint [1] '''
            endElement=ET.SubElement(simElement,'endPoint')
            ''' endPoint element has an optional start date and an option end date '''
            ''' documentID [1] '''
            ET.SubElement(simElement,'documentID').text=simClass.uri
            ''' documentAuthor [0..inf] '''
            authorElement=ET.SubElement(simElement,'documentAuthor')
            self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
            ''' documentCreationDate [1] '''
            ET.SubElement(simElement,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
            ''' documentGenealogy [0..inf] '''
            ''' quality [0..inf] '''
            if not(self.VALIDCIMONLY):
                ET.SubElement(simElement,'Q_AuthorList').text=simClass.authorList

        else :
            #set simClass so that we know to pick up any simulation couplings
            self.simClass=simClass
            simElement=ET.SubElement(rootElement,'Q_Simulation')
            #Simulation isa Doc
            self.addDoc(simClass,simElement)
            modelElement=ET.SubElement(simElement,'Q_NumericalModel')
            self.add_component(simClass.numericalModel,modelElement)
            ET.SubElement(simElement,'Q_EnsembleCount').text=str(simClass.ensembleMembers)
            # add ensemble information from Ensemble class
            # There should be a one to one mapping but we can not be sure here
            ensemblesElement=ET.SubElement(simElement,'Q_Ensembles')
            ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
            assert(len(ensembleClassSet)==1,'Simulation %s should have one and only one associated ensembles class'%simClass)
            for ensembleClass in ensembleClassSet :
                self.addEnsemble(ensembleClass,ensemblesElement)
            self.add_experiment(simClass.experiment,simElement)
            self.add_platform(simClass.platform,simElement)
            self.addCentre(simClass.centre,simElement)
            ET.SubElement(simElement,'Q_AuthorList').text=simClass.authorList
            modelModsElement=ET.SubElement(simElement,'Q_ModelMods')
            for modelModClass in simClass.modelMod.all():
                self.addModelMod(modelModClass,modelModsElement)
            inputModsElement=ET.SubElement(simElement,'Q_InputMods')
            for inputModClass in simClass.inputMod.all():
                self.addInputMod(inputModClass,inputModsElement)
            # add any associated files here for the moment
            filesElement=ET.SubElement(simElement,'Q_Files')
            # CouplingGroup does not appear to hold a component or simulations files.
            # returning all datacontainers (files) associated with this centre
            filesElement.append(ET.Comment("CouplingGroup does not appear to contain files associated with a component or simulation. Returning all datacontainers (files) associated with this centre as a fallback."))
            dataContainerInstanceSet=DataContainer.objects.filter(centre=simClass.centre)
            for dataContainerInstance in dataContainerInstanceSet:
                self.addDataContainer(dataContainerInstance,filesElement)
        return rootElement


    def addModificationRef(self,modClass,rootElement) :
        if modClass :
            modRefElement=ET.SubElement(rootElement,'Q_ModificationRef')
            if (self.CIMXML) :
                modRefElement.append(ET.Comment("WARNING: Modification information still needs to be added."))
            else :
                modRefElement.append(ET.Comment("I can not find a simple way to determine whether the modification is of type ModelMod or InputMod so I just store the modification name and type here as a reference. We can look up the details of the actual modification as they are stored with the simulation."))

            ET.SubElement(modRefElement,'Q_Name').text=modClass.mnemonic
            if modClass.mtype:
                ET.SubElement(modRefElement,'Q_Type').text=modClass.mtype.value

    def addModification(self,modClass,rootElement) :
        if modClass :
            modElement=ET.SubElement(rootElement,'Q_Modification')
            ET.SubElement(modElement,'Q_Mnemonic').text=modClass.mnemonic
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
            if couplingClass.targetInput:
                if couplingClass.targetInput.owner:
                    ET.SubElement(couplingElement,'Q_ComponentName').text=couplingClass.targetInput.owner.abbrev
                if couplingClass.targetInput.realm:
                    ET.SubElement(couplingElement,'Q_RealmName').text=couplingClass.targetInput.realm.abbrev
                ET.SubElement(couplingElement,'Q_AttrName').text=couplingClass.targetInput.abbrev
                if couplingClass.targetInput.ctype:
                    ET.SubElement(couplingElement,'Q_Type').text=couplingClass.targetInput.ctype.value

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
            if self.CIMXML :
                if reqClass.ctype :
                    reqElement=ET.SubElement(rootElement,'numericalRequirement',{self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+'type':reqClass.ctype.value})
                else :
                    reqElement=ET.SubElement(rootElement,'numericalRequirement')
                ''' numericalRequirement [0..inf] '''
                ''' id [1] '''
                ET.SubElement(reqElement,'id').text='[TBD]'                
                ''' name [1] '''
                ET.SubElement(reqElement,'name').text=reqClass.name
                ''' description [0,1] '''
                ET.SubElement(reqElement,'description').text=reqClass.description
                if not(self.VALIDCIMONLY) :
                    valueElement=ET.SubElement(reqElement,'Q_CtypeValue')
                    self.addValue(reqClass.ctype,valueElement)
                    confElement=ET.SubElement(reqElement,'Q_Conformances')
                    confClassSet=Conformance.objects.filter(requirement=reqClass)
                    for confClass in confClassSet:
                        self.addConformance(confClass,confElement)
            else :
                reqElement=ET.SubElement(rootElement,'Q_NumericalRequirement')
                ET.SubElement(reqElement,'Q_Description').text=reqClass.description
                ET.SubElement(reqElement,'Q_Name').text=reqClass.name
                valueElement=ET.SubElement(reqElement,'Q_CtypeValue')
                self.addValue(reqClass.ctype,valueElement)
                confElement=ET.SubElement(reqElement,'Q_Conformances')
                confClassSet=Conformance.objects.filter(requirement=reqClass)
                for confClass in confClassSet:
                    self.addConformance(confClass,confElement)
        
    def addConformance(self,confClass,rootElement):
        if confClass :
            confElement=ET.SubElement(rootElement,'Q_Conformance')
            valueElement=ET.SubElement(confElement,'Q_CtypeValue')
            self.addValue(confClass.ctype,valueElement)
            modsElement=ET.SubElement(confElement,'Q_ModelModifications')
            for modClass in confClass.mod.all():
                # reference the code modification here to avoid replication as it is stored as part of the simulation
                self.addModificationRef(modClass,modsElement)
            coupElement=ET.SubElement(confElement,'Q_InputBindings')
            for coupClass in confClass.coupling.all():
                self.addCouplingRef(coupClass,coupElement)
            ET.SubElement(confElement,'Q_Description').text=confClass.description

    def add_experiment(self,expClass,rootElement):
        if (self.CIMXML):
            expElement=ET.SubElement(rootElement,'numericalExperiment',{'CIMVersion': '1.4'})
            ''' responsibleParty [0..inf] '''
            ''' principleInvestigator [0..inf] '''
            ''' fundingSource [0..inf] '''
            ''' rationale [1..inf] '''
            ET.SubElement(expElement,'rationale').text=expClass.rationale
            ''' measurementCampaign [0..inf] '''
            ''' requires [0..inf] '''
            ''' generates [0..inf] '''
            ''' experimentID [0..1] '''
            ''' duration [0..1] '''
            ''' numericalRequirement [1..inf] '''
            for reqClass in expClass.requirements.all():
                self.addRequirement(reqClass,expElement)
            ''' supports [0..inf] '''
            ''' shortName [1] '''
            ET.SubElement(expElement,'shortName').text=expClass.abbrev
            ''' longName [1] '''
            ET.SubElement(expElement,'longName').text=expClass.title
            ''' description [0..1] '''
            ET.SubElement(expElement,'description').text=expClass.description
            ''' calendar [1] '''
            calendarElement=ET.SubElement(expElement,'calendar')
            assert(expClass.requiredCalendar)
            calTypeElement=ET.SubElement(calendarElement,str(expClass.requiredCalendar.value))
            rangeElement=ET.SubElement(calTypeElement,'range')
            ET.SubElement(rangeElement,'closedDateRange')
            ''' requiredDuration [1] '''
            assert(expClass.requiredDuration)
            durationElement=ET.SubElement(expElement,'requiredDuration')
            ET.SubElement(durationElement,'startDate').text=expClass.requiredDuration.startDate
            ET.SubElement(durationElement,'endDate').text=expClass.requiredDuration.endDate
            if not(self.VALIDCIMONLY) :
                ET.SubElement(expElement,'Q_lengthYears').text=str(expClass.requiredDuration.length)
            ''' documentID [1] '''
            ET.SubElement(expElement,'documentID').text=expClass.uri
            ''' documentAuthor [0..inf] '''
            authorElement=ET.SubElement(expElement,'documentAuthor')
            self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
            ''' documentCreationDate [1] '''
            ET.SubElement(expElement,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
            ''' documentGenealogy [0..inf] '''
            ''' quality [0..inf] '''

        else :
            expElement=ET.SubElement(rootElement,'Q_Experiment')
            ET.SubElement(expElement,'Q_Rationale').text=expClass.rationale
            ET.SubElement(expElement,'Q_Description').text=expClass.description
            reqsElement=ET.SubElement(expElement,'Q_NumericalRequirements')
            for reqClass in expClass.requirements.all():
                self.addRequirement(reqClass,reqsElement)
            ET.SubElement(expElement,'Q_DocID').text=expClass.docID
            ET.SubElement(expElement,'Q_ShortName').text=expClass.shortName
            ET.SubElement(expElement,'Q_LongName').text=expClass.longName
            durationElement=ET.SubElement(expElement,'Q_Duration')
            ET.SubElement(durationElement,'Q_StartDate').text=expClass.startDate
            ET.SubElement(durationElement,'Q_EndDate').text=expClass.endDate
            ET.SubElement(durationElement,'Q_length').text=str(expClass.length)
            ET.SubElement(durationElement,'Q_calendar').text=str(expClass.calendar)

    def setComponentOptions(self,recurse,composition):

        self.recurse=recurse
        self.outputComposition=composition
    
    def add_component(self,compClass,rootElement):

        assert(compClass)
        if compClass :
            self.addChildComponent(compClass,rootElement,1,self.recurse)
        return rootElement

    def addComponentDoc(self,docClass,rootElement):

        if docClass :
            docElement=ET.SubElement(rootElement,'Q_Doc')
            self.addResp(docClass.metadataMaintainer,docElement,'metadataMaintainer')
            ET.SubElement(docElement,'Q_MetadataVersion').text=docClass.metadataVersion
            ET.SubElement(docElement,'Q_DocumentVersion').text=str(docClass.documentVersion)
            ET.SubElement(docElement,'Q_Created').text=str(docClass.created)
            ET.SubElement(docElement,'Q_Updated').text=str(docClass.updated)


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
        

    def add_platform(self,platClass,rootElement):

        if platClass :
            if (self.CIMXML) :
                deployElement=ET.SubElement(rootElement,'deployment')
                if not(self.VALIDCIMONLY):
                    #no funder specified for deployments in the questionnaire
                    #self.addResp(docClass.author,docElement,'author')
                    self.addResp(platClass.funder,deployElement,'funder')
                    self.addResp(platClass.contact,deployElement,'contact')
                ''' deploymentDate [1] '''
                # deploymentDate is now optional
                #ET.SubElement(deployElement,'deploymentDate').text='0001-01-01T00:00:00'
                ''' description [0..1] '''
                ''' platform [1] '''
                platformElement=ET.SubElement(deployElement,'platform')
                machineElement=ET.SubElement(platformElement,'machine')
                # platClass.title is never set
                ET.SubElement(machineElement,'machineName').text=platClass.abbrev
                if platClass.hardware :
                    ET.SubElement(machineElement,'machineSystem').text=platClass.hardware.value
                else:
                    ET.SubElement(machineElement,'machineSystem')
                #ET.SubElement(machineElement,'machineLibrary')
                ET.SubElement(machineElement,'machineDescription').text=platClass.description
                #ET.SubElement(machineElement,'machineLocation')
                if platClass.operatingSystem :
                    machOSEl=ET.SubElement(machineElement,'machineOperatingSystem',{'value':platClass.operatingSystem.value})
                    vsEl=ET.SubElement(machOSEl,'vocabularyServer')
                    ET.SubElement(vsEl,'vocabularyName')
                if platClass.vendor :
                    ET.SubElement(machineElement,'machineVendor').text=platClass.vendor.value
                if platClass.interconnect :
                    ET.SubElement(machineElement,'machineInterconnect').text=platClass.interconnect.value
                ET.SubElement(machineElement,'machineMaximumProcessors').text=str(platClass.maxProcessors)
                ET.SubElement(machineElement,'machineCoresPerProcessor').text=str(platClass.coresPerProcessor)
                if platClass.processor :
                    ET.SubElement(machineElement,'machineProcessorType').text=platClass.processor.value
                ''' compiler [1..inf] '''
                compilerElement=ET.SubElement(platformElement,'compiler')
                if platClass.compiler :
                    ET.SubElement(compilerElement,'compilerName').text=platClass.compiler.value
                ET.SubElement(compilerElement,'compilerVersion').text=platClass.compilerVersion
                ET.SubElement(compilerElement,'compilerLanguage')
                #ET.SubElement(compilerElement,'compilerOptions')
                #ET.SubElement(compilerElement,'compilerEnvironmentVariables')
                #ET.SubElement(compilerElement,'compilerLibrary')
                ''' documentID [1] '''
                ET.SubElement(deployElement,'documentID').text=platClass.uri
                ''' documentAuthor [0] '''
                #ET.SubElement(comp,'documentAuthor').text=c.contact
                authorElement=ET.SubElement(deployElement,'documentAuthor')
                self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
                ''' documentCreationDate [1] '''
                ET.SubElement(deployElement,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
                ''' documentGenealogy [0] '''
                ''' quality [0..inf] '''
            else :
                platElement=ET.SubElement(rootElement,'Q_Platform')
                #Platform isa Doc
                self.addDoc(platClass,platElement)
                # add centre info ???
                ET.SubElement(platElement,'Q_Compiler').text=platClass.compiler
                ET.SubElement(platElement,'Q_Vendor').text=platClass.vendor
                ET.SubElement(platElement,'Q_CompilerVersion').text=platClass.compilerVersion
                ET.SubElement(platElement,'Q_MaxProcessors').text=str(platClass.maxProcessors)
                ET.SubElement(platElement,'Q_CoresPerProcessor').text=str(platClass.coresPerProcessor)
                ET.SubElement(platElement,'Q_OperatingSystem').text=platClass.operatingSystem
                hardwareElement=ET.SubElement(platElement,'Q_HardwareVal')
                self.addValue(platClass.hardware,hardwareElement)
                processorElement=ET.SubElement(platElement,'Q_ProcessorVal')
                self.addValue(platClass.processor,processorElement)
                interconnectElement=ET.SubElement(platElement,'Q_InterconnectVal')
                self.addValue(platClass.interconnect,interconnectElement)
        return rootElement

    def constraintValid(self,con,constraintSet) :
        if con.constraint=='' : # there is no constraint
            return True
        else : # need to check the constraint
            # constraint format is : if <ParamName> [is|has] [not]* "<Value>"[ or "<Value>"]*
            #ET.SubElement(conElement,'Q_Constraint').text=con.constraint
            parsed=con.constraint.split()
            assert(parsed[0]=='if','Error in constraint format')
            assert(parsed[2]=='is' or parsed[2]=='has','Error in constraint format')
            paramName=parsed[1]
            #ET.SubElement(conElement,'Q_Constraint_Param').text=paramName
            if parsed[2]=='is' :
                singleValueExpected=True
            else:
                singleValueExpected=False
            #ET.SubElement(conElement,'Q_Constraint_SingleValuedParam').text=str(singleValueExpected)
            if parsed[3]=='not' :
                negation=True
                idx=4
            else :
                negation=False
                idx=3
            #ET.SubElement(conElement,'Q_Constraint_Negation').text=str(negation)
            nValues=0
            valueArray=[]
            while idx<len(parsed) :
                valueArray.append(parsed[idx].strip('"'))
                nValues+=1
                if (idx+1)<len(parsed) :
                    assert(parsed[idx+1]=='or','Error in constraint format')
                idx+=2
            assert(nValues>0)
            #ET.SubElement(conElement,'Q_Constraint_nValues').text=str(nValues)
            #for value in valueArray :
            #    ET.SubElement(conElement,'Q_Constraint_value').text=value

            # now check if the constraint is valid or not
            # first find the value(s) of the parameter that is referenced
            found=False
            refValue=''
            for con in constraintSet:
                if not(found):
                    pset=NewParam.objects.filter(constraint=con)
                    for p in pset:
                        if (p.name==paramName) :
                            found=True
                            refValue=p.value
            assert(found,'Error, can not find property that is referenced by constraint')
            #ET.SubElement(conElement,'Q_Constraint_RefValues').text=refValue
            if refValue=='' : # the reference parameter does not have any values set
                return True # output constraint parameters if the reference parameter is not set. This is an arbitrary decision, I could have chosen not to.
            match=False
            for value in refValue.split('|'):
                if not(match) :
                    stripSpaceValue=value.strip()
                    if stripSpaceValue != '' :
                        if stripSpaceValue in valueArray :
                            match=True
            #ET.SubElement(conElement,'Q_Constraint_Match').text=str(match)
            if negation :
                match=not(match)
            return match


    def addChildComponent(self,c,root,nest,recurse=True):

      if c.implemented or nest==1:
        if nest==1:
          # documentVersion has been removed since CIM1.3 (current is CIM1.4)
          #comp=ET.SubElement(root,'modelComponent',{'documentVersion': str(c.documentVersion), 'CIMVersion': '1.4'})
          comp=ET.SubElement(root,'modelComponent',{'CIMVersion': '1.4'})
        else:
          comp=ET.SubElement(root,'modelComponent')
        '''composition'''
        self.composition(c,comp)
        if recurse:
            '''childComponent'''
            for child in c.components.all():
                if child.implemented:
                    comp2=ET.SubElement(comp,'childComponent')
                    self.addChildComponent(child,comp2,nest+1)
                else :
                    comp.append(ET.Comment('Component '+child.abbrev+' has implemented set to false'))
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
                # the internal questionnaire representation is that all parameters
                # are contained in a constraint group
                for con in constraintSet:
                    if con.constraint!='' :
                        componentProperty.append(ET.Comment('Constraint : '+con.constraint))
                    if self.constraintValid(con,constraintSet) :
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
                '''shortName'''
                ET.SubElement(componentProperty,'shortName').text=pg.name
                '''longName'''
                ET.SubElement(componentProperty,'longName').text=pg.name
                
        '''numericalProperties'''
        ET.SubElement(comp,'numericalProperties')
        '''scientificProperties'''
        ET.SubElement(comp,'scientificProperties')
        '''grid'''
        '''responsibleParty'''
        self.addResp(c.author,comp,'author')
        self.addResp(c.funder,comp,'funder')
        self.addResp(c.contact,comp,'contact')
        self.addResp(c.centre.party,comp,'centre')
        '''fundingSource'''
        '''citation'''
        self.addReferences(c.references,comp)
        ''' RF associating genealogy with the component rather than the document '''
        if (nest<=2 and not(self.VALIDCIMONLY)):
            genealogy=ET.SubElement(comp,'Q_genealogy')
            ET.SubElement(genealogy,'Q_yearReleased').text=str(c.yearReleased)
            ET.SubElement(genealogy,'Q_previousVersion').text=c.otherVersion
            ET.SubElement(genealogy,'Q_previousVersionImprovements').text=c.geneology


        '''activity'''
        '''type'''
        #comp.append(ET.Comment("value attribute in element type should have value "+c.scienceType+" but this fails the cim validation at the moment"))
        #ET.SubElement(comp,'type',{'value':'other'}) # c.scienceType
        typeElement=ET.SubElement(comp,'type',{'value':c.scienceType})
        #CIM1.4 requires at least one server subelement for validation even if it is empty i.e. does nothing
        vsElement=ET.SubElement(typeElement,'vocabularyServer')
        ET.SubElement(vsElement,'vocabularyName')
        '''component timestep info not explicitely supplied in questionnaire'''
        #if nest==2:
                #timing=ET.SubElement(comp,'timing',{'units':'units'})
                #ET.SubElement(timing,'rate').text='rate'
        if nest==1:
            '''documentID'''
            ET.SubElement(comp,'documentID').text=c.uri
            '''documentAuthor'''
            #ET.SubElement(comp,'documentAuthor').text=c.contact
            authorElement=ET.SubElement(comp,'documentAuthor')
            self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
            '''documentCreationDate'''
            #ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())
            ET.SubElement(comp,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
            '''documentGenealogy'''
            # component genealogy is provided in the questionnaire
            '''quality'''
            # no quality information in the questionnaire at the moment
          

      else:
          root.append(ET.Comment('Component '+c.abbrev+' has implemented set to false'))
        #logging.debug("component "+c.abbrev+" has implemented set to false")
      return

    def addReferences(self,references,rootElement):
        for ref in references.all():
            self.addReference(ref,rootElement)

    def addReference(self,refInstance,rootElement):
        if refInstance :
            if self.CIMXML :
                refElement=ET.SubElement(rootElement,'citation')
                citeElement=ET.SubElement(refElement,self.GMD_NAMESPACE_BRACKETS+'CI_Citation')
                titleElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'title')
                ET.SubElement(titleElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=refInstance.name
                # CIM expects a date element even if it is empty
                ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'date')
                presElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'presentationForm')
                ET.SubElement(presElement,self.GMD_NAMESPACE_BRACKETS+'CI_PresentationFormCode',{'codeList':'','codeListValue':str(refInstance.refType)})
                ociteElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'otherCitationDetails')
                ET.SubElement(ociteElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=refInstance.link
                ctElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'collectiveTitle')
                ET.SubElement(ctElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=refInstance.citation
            else :
                refElement=ET.SubElement(rootElement,'Q_reference')
                ET.SubElement(refElement,'Q_name').text=refInstance.name
                ET.SubElement(refElement,'Q_citation').text=refInstance.citation
                ET.SubElement(refElement,'Q_link').text=refInstance.link
                if refInstance.refValue :
                    ET.SubElement(refElement,'Q_refType').text=refInstance.refType.value

    def addSimpleResp(self,respName,rootElement,respType) :
        ciresp=ET.SubElement(rootElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
        ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respName
        role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')
        ET.SubElement(role,self.GMD_NAMESPACE_BRACKETS+'CI_RoleCode',{'codeList':'', 'codeListValue':respType})


    def addResp(self,respClass,rootElement,respType):
        if (respClass) :
            if not(self.CIMXML) :

                respElement=ET.SubElement(rootElement,"Q_responsibleParty",{'type':respType})
                ET.SubElement(respElement,"Q_name").text=respClass.name
                ET.SubElement(respElement,"Q_webpage").text=respClass.webpage
                ET.SubElement(respElement,"Q_abbrev").text=respClass.abbrev
                ET.SubElement(respElement,"Q_email").text=respClass.email
                ET.SubElement(respElement,"Q_address").text=respClass.address
                ET.SubElement(respElement,"Q_uri").text=respClass.uri
            else :
                if respClass.name == 'Unknown' : # skip the default respobject
                    rootElement.append(ET.Comment('responsibleParty '+respType+ ' is set to unknown. No CIM output will be generated.'))
                    return
                respElement=ET.SubElement(rootElement,'responsibleParty')
                respElement.append(ET.Comment('responsibleParty uri :: '+respClass.uri))
                ciresp=ET.SubElement(respElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        #name=ET.SubElement(resp,'gmd:individualName')
        #ET.SubElement(name,'gco:CharacterString').text=c.contact
                if respType=='author' or respType=='contact' :
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
                else: # default to organisation if not a contact or an author
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'organisationName')
                ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.name
                name.append(ET.Comment('responsibleParty abbreviation :: '+respClass.abbrev))
        #</gmd:individualName/>
        # <gmd:organisationName/>
        # <gmd:positionName/>
        # <gmd:contactInfo>
        #contact=ET.SubElement(ciresp,'gmd:contactInfo')
                contact=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'contactInfo')
                cicontact=ET.SubElement(contact,self.GMD_NAMESPACE_BRACKETS+'CI_Contact')
        #     <gmd:phone/>
        #     <gmd:address>
        #address=ET.SubElement(cicontact,'gmd:address')
                address=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'address')
                ciaddress=ET.SubElement(address,self.GMD_NAMESPACE_BRACKETS+'CI_Address')
        #         <gmd:deliveryPoint/>
                address=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'deliveryPoint')
                ET.SubElement(address,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.address
        #         <gmd:city/>
        #         <gmd:administrativeArea/>
        #         <gmd:postalCode/>
        #         <gmd:country/>
        #         <gmd:electronicMailAddress>
        #email=ET.SubElement(ciaddress,'gmd:electronicMailAddress')
        #ET.SubElement(email,'gco:CharacterString').text=c.email
                email=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'electronicMailAddress')
                ET.SubElement(email,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.email
        #         </gmd:electronicMailAddress>
        #     </gmd:address>
        #     <gmd:onlineResource/>
                resource=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'onlineResource')
                ciresource=ET.SubElement(resource,self.GMD_NAMESPACE_BRACKETS+'CI_OnlineResource')
                linkage=ET.SubElement(ciresource,self.GMD_NAMESPACE_BRACKETS+'linkage')
                url=ET.SubElement(linkage,self.GMD_NAMESPACE_BRACKETS+'URL').text=respClass.webpage
        #     <gmd:hoursOfService/>
        #     <gmd:contactInstructions/>
        # </gmd:contactInfo>
        # <gmd:role/>
                role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')
                ET.SubElement(role,self.GMD_NAMESPACE_BRACKETS+'CI_RoleCode',{'codeList':'', 'codeListValue':respType})

    def composition(self,c,comp):
        couplings=[]
        # couplings are all at the esm (root component) level
        if c.isModel:couplings=c.couplings(simulation=self.simClass)
        if len(couplings)>0 and self.CIMXML :
            if self.outputComposition :
                composeElement=ET.SubElement(comp,'composition')
                for coupling in couplings:
                    # output each link separately as the questionnaire keeps information
                    # about transformations on a link by link basis
                    extclosures=ExternalClosure.objects.filter(coupling=coupling)
                    for closure in extclosures :
                        self.addCoupling(coupling,closure,composeElement)
                    intclosures=InternalClosure.objects.filter(coupling=coupling)
                    for closure in intclosures :
                        self.addCoupling(coupling,closure,composeElement)
                ET.SubElement(composeElement,'description').text='Input coupling details for component '+c.abbrev
            else :
                comp.append(ET.Comment('Coupling information exists but its output has been switched off for this CIM Object'))

        elif len(couplings)>0 :
            composeElement=ET.SubElement(comp,'composition')
            for coupling in couplings:
                CompInpClass=coupling.targetInput
                assert(CompInpClass,'A Coupling instance must have an associated ComponentInput instance')
                assert(CompInpClass.owner,'A Coupling instance must have an associated ComponentInput instance with a valid owner')
                assert(CompInpClass.realm,'A Coupling instance must have an associated ComponentInput instance with a valid realm')
                assert(CompInpClass.ctype,'A Coupling instance must have an associated ComponentInput instance with a valid ctype')
                couplingElement=ET.SubElement(composeElement,'coupling')
                ET.SubElement(couplingElement,'Q_sourceComponent').text=CompInpClass.owner.abbrev
                ET.SubElement(couplingElement,'Q_realmComponent').text=CompInpClass.realm.abbrev
                ET.SubElement(couplingElement,'Q_inputType').text=CompInpClass.ctype.value
                ET.SubElement(couplingElement,'Q_inputAbbrev').text=CompInpClass.abbrev
                ET.SubElement(couplingElement,'Q_inputDescrip').text=CompInpClass.description
                if CompInpClass.ctype.value=='BoundaryCondition':
                    if (coupling.ctype):
                        ET.SubElement(couplingElement,'Q_type').text=coupling.ctype.value
                    else:
                        ET.SubElement(couplingElement,'Q_type')
                    if (coupling.FreqUnits):
                        ET.SubElement(couplingElement,'Q_freqUnits').text=coupling.FreqUnits.value
                    else:
                        ET.SubElement(couplingElement,'Q_freqUnits')
                    ET.SubElement(couplingElement,'Q_frequency').text=str(coupling.couplingFreq)
                    ET.SubElement(couplingElement,'Q_manipulation').text=coupling.manipulation
                iClosures=InternalClosure.objects.filter(coupling=coupling)
                if len(iClosures)>0:
                    closures=ET.SubElement(couplingElement,'Q_internalClosures')
                    for iclos in iClosures:
                        closure=ET.SubElement(closures,'Q_closure')
                        if iclos.spatialRegridding:
                            ET.SubElement(closure,'Q_spatialRegridding').text=iclos.spatialRegridding.value
                        if iclos.spatialType:
                            ET.SubElement(closure,'Q_spatialType').text=iclos.spatialType.value
                        if iclos.temporalRegridding:
                            ET.SubElement(closure,'Q_temporalRegridding').text=iclos.temporalRegridding.value
                        ET.SubElement(closure,'Q_inputDescription').text=iclos.inputDescription
                        if iclos.target:
                            ET.SubElement(closure,'Q_target').text=iclos.target.abbrev
                eClosures=ExternalClosure.objects.filter(coupling=coupling)
                if len(eClosures)>0:
                    closures=ET.SubElement(couplingElement,'Q_externalClosures')
                    for ExtClosClass in eClosures:
                        closure=ET.SubElement(closures,'Q_closure')
                        ET.SubElement(closure,'Q_spatialRegridding').text=ExtClosClass.spatialRegridding.value
                        ET.SubElement(closure,'Q_spatialType').text=ExtClosClass.spatialType.value
                        ET.SubElement(closure,'Q_temporalRegridding').text=ExtClosClass.temporalRegridding.value
                        ET.SubElement(closure,'Q_inputDescription').text=ExtClosClass.inputDescription
                        #Data is output separately so reference it at this point
                        self.addDataRef(ExtClosClass.target,closure)
                        
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

    def addCoupling(self,coupling,closure,composeElement) :
        CompInpClass=coupling.targetInput
        assert CompInpClass,'A Coupling instance must have an associated ComponentInput instance'
        assert CompInpClass.owner,'A Coupling instance must have an associated ComponentInput instance with a valid owner'
        assert CompInpClass.ctype,'A Coupling instance must have an associated ctype value'
        couplingType=CompInpClass.ctype.value
        if couplingType=='BoundaryCondition' :
            couplingType='boundaryCondition'
        elif couplingType=='AncillaryFile' :
            couplingType='forcing'
        elif couplingType=='InitialCondition' :
            couplingType='initialForcing'
        couplingElement=ET.SubElement(composeElement,'coupling',{'purpose':couplingType,'fullySpecified':'false'})
        '''connection'''
        '''description'''
        ET.SubElement(couplingElement,'description').text=coupling.manipulation
        '''timeProfile'''
        units=''
        if coupling.FreqUnits :
            units=str(coupling.FreqUnits.value)
        if units!='' or coupling.couplingFreq!=None :
            tpElement=ET.SubElement(couplingElement,'timeProfile',{'units':units})
            #ET.SubElement(tpElement,'start')
            #ET.SubElement(tpElement,'end')
            ET.SubElement(tpElement,'rate').text=str(coupling.couplingFreq)
        if coupling.inputTechnique :
            tpElement.append(ET.Comment('input technique :: '+coupling.inputTechnique.value))
        '''timeLag'''
        '''spatialRegridding'''
        if closure.spatialRegrid :
            ET.SubElement(couplingElement,'spatialRegridding').text=closure.spatialRegrid.value
            ''' conservativespatialregridding t/f '''
        '''timeTransformation'''
        if closure.temporalTransform :
            ''' timeaverage t/f, timeaccumulation t/f '''
            ET.SubElement(couplingElement,'timeTransformation').text=closure.temporalTransform.value
        '''couplingSource'''
        sourceElement=ET.SubElement(couplingElement,'couplingSource')
        if closure.target :
            self.addCIMReference(closure.target,sourceElement)
        else :
            try :
                self.addCIMReference(closure.targetFile,sourceElement)
            except :
                sourceElement.append(ET.Comment('error: couplingSource closure has no target and (for ExternalClosures) no targetFile'))
        '''couplingTarget'''
        targetElement=ET.SubElement(couplingElement,'couplingTarget')
        self.addCIMReference(CompInpClass.owner,targetElement)
        '''priming'''

    def addDataRef(self,dataObjectClass,rootElement):
        assert(dataObjectClass,'dataObject should not be null')
        assert(dataObjectClass.container,'dataContainer should not be null')
        dataRefElement=ET.SubElement(rootElement,"Q_DataRef")
        ET.SubElement(dataRefElement,"Q_VariableName").text=dataObjectClass.variable
        ET.SubElement(dataRefElement,"Q_FileName").text=dataObjectClass.container.name

    def addDataContainer(self,dataContainerClass,rootElement):
        if dataContainerClass :
            dataContainerElement=ET.SubElement(rootElement,"Q_dataContainer")
            ET.SubElement(dataContainerElement,"Q_Name").text=dataContainerClass.name
            ET.SubElement(dataContainerElement,"Q_URL").text=dataContainerClass.link
            ET.SubElement(dataContainerElement,"Q_Description").text=dataContainerClass.description
            formatElement=ET.SubElement(dataContainerElement,'Q_FormatVal')
            self.addValue(dataContainerClass.format,formatElement)
            self.addReference(dataContainerClass.reference,dataContainerElement)
            # add any associated data
            dataObjectsElement=ET.SubElement(dataContainerElement,'Q_DataObjects')
            dataObjectInstanceSet=DataObject.objects.filter(container=dataContainerClass)
            for dataObjectInstance in dataObjectInstanceSet:
                self.addDataObject(dataObjectInstance,dataObjectsElement)

    def addDataObject(self,dataObjectClass,rootElement):
        assert(dataObjectClass,'dataObject should not be null')
        dataElement=ET.SubElement(rootElement,"Q_DataObject")
        ET.SubElement(dataElement,"Q_description").text=dataObjectClass.description
        ET.SubElement(dataElement,"Q_variable").text=dataObjectClass.variable
        ET.SubElement(dataElement,"Q_cfname").text=dataObjectClass.cftype
        self.addReference(dataObjectClass.reference,dataElement)
        # dataClass.featureType is unused at the moment
        # dataClass.drsAddress is unused at the moment

    def addCIMReference(self,rootClass,rootElement):
        if rootClass._meta.module_name=='dataobject' :
            # special case as I am not a document
            try :
                myURI=rootClass.container.uri
                myDocumentVersion=rootClass.container.documentVersion
            except :
                # datafile not yet implemented as a document
                myURI='TBAforDataFiles'
                myDocumentVersion='0'
            if rootClass.variable!='' :
                myName=rootClass.variable
            else :
                myName='NoneSpecified'
        else :
            try :
                myURI=rootClass.uri
                myDocumentVersion=rootClass.documentVersion
                myName=rootClass.abbrev
            except :
                myURI='TBD'
                myDocumentVersion='0'
                myName='TBD'


        targetRef=ET.SubElement(rootElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':'#//CIMRecord[id=\''+myURI+'\']'})
        ''' id '''
        ET.SubElement(targetRef,'id').text=myURI
        ''' name '''
        ET.SubElement(targetRef,'name').text=myName
        ''' type '''
        try :
            targetRef.append(ET.Comment('type: '+rootClass._meta.module_name))
        except :
            targetRef.append(ET.Comment('type: ERROR'))
        ''' version '''
        ET.SubElement(targetRef,'version').text=str(myDocumentVersion)
        ''' description '''
        ET.SubElement(targetRef,'description').text='Reference to a '+rootClass._meta.module_name+' called '+myName
        #ET.SubElement(expReference,'description').text='The experiment to which this simulation conforms'

    def add_dataobject(self,fileClass,rootElement):

        if fileClass :
            doElement=ET.SubElement(rootElement,'dataObject',{'dataStatus':'complete'})
            doElement.append(ET.Comment('ABBREVIATION: '+fileClass.abbrev))
            doElement.append(ET.Comment('DESCRIPTION: '+fileClass.description))
            storeElement=ET.SubElement(doElement,'storage')
            lfElement=ET.SubElement(storeElement,'ipStorage',{'dataFormat':fileClass.format.value,'dataLocation':''})
            ET.SubElement(lfElement,'dataSize').text='0'
            ET.SubElement(lfElement,'protocol')
            ET.SubElement(lfElement,'host')
            ET.SubElement(lfElement,'path').text=fileClass.link
            ET.SubElement(lfElement,'fileName').text=fileClass.name

            distElement=ET.SubElement(doElement,'distribution',{'distributionFormat':fileClass.format.value,'distributionAccess':'OnlineFileHTTP'})
            ET.SubElement(distElement,'distributionFee')
            ET.SubElement(distElement,'responsibleParty')

            self.addReference(fileClass.reference,doElement)
            for variable in DataObject.objects.filter(container=fileClass) :
                contentElement=ET.SubElement(doElement,'content')
                contentElement.append(ET.Comment('DESCRIPTION: '+variable.description))
                if variable.cfname :
                    ET.SubElement(contentElement,'topic').text=variable.cfname.value
                    contentElement.append(ET.Comment('non-cfname: '+variable.variable))
                elif variable.variable!='' :
                    ET.SubElement(contentElement,'topic').text=variable.variable
                unitElement=ET.SubElement(contentElement,'unit',{'value':'other'})
                vocabElement=ET.SubElement(unitElement,'vocabularyServer')
                ET.SubElement(vocabElement,'vocabularyName')
                ET.SubElement(contentElement,'aggregation')
                ET.SubElement(contentElement,'frequency')

                if variable.reference :
                    contentElement.append(ET.Comment('ARGHHH: there is a reference'))
                # not used in questionnaire : featureType, drsAddress
            ''' documentID '''
            try :
                ET.SubElement(doElement,'documentID').text=fileClass.uri
            except :
                ET.SubElement(doElement,'documentID').text='00000000-0000-0000-0000-000000000000'
            ET.SubElement(doElement,'documentCreationDate').text=str(datetime.date.today())+'T00:00:00'
