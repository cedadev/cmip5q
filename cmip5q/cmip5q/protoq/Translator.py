
from cmip5q.protoq.models import *

from lxml import etree as ET
import uuid
import datetime

from django.conf import settings
logging=settings.LOG


class Translator:


    ''' Translates a questionnaire Doc class (Simulation, Component, (Ensemble) or Platform) into a CIM document (as an lxml etree instance) '''

    # only valid CIM will be output if the following is set to true. This means that all information will not be output as some does not align with the CIM structure (ensembles and genealogy in particular).
    VALIDCIMONLY=True

    CIM_NAMESPACE = "http://www.metaforclimate.eu/schema/cim/1.5"
    SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_INSTANCE_NAMESPACE_BRACKETS = "{"+SCHEMA_INSTANCE_NAMESPACE+"}"
    CIM_URL = CIM_NAMESPACE+"/"+"cim.xsd"
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
        ''' provide a textual (html) view of the status of a component '''
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

        for pg in c.paramGroup.all().order_by('id'):
            constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
            for con in constraintSet:
                #
                # we need to keep the parameters in the same order
                # as they are in the questionnaire. Therefore we can
                # not treat XOR, then OR, then KeyBoard. I don't know
                # how to determine a derived class from a base class.
                # So here is a rubbish solution that works!
                #
                # Needed to add .order_by('id') as the database does not guarantee
                # to return objects in the same order, hence the order of the baseclass
                # objects might not be the same as the Xor, Or, or KeyBoard objects
                # whereas this code assumes the same order.
                #
                BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                XorParamSet=XorParam.objects.filter(constraint=con).order_by('id')
                OrParamSet=OrParam.objects.filter(constraint=con).order_by('id')
                KeyBoardParamSet=KeyBoardParam.objects.filter(constraint=con).order_by('id')
                XorIDX=0
                OrIDX=0
                KeyBoardIDX=0
                for bp in BaseParamSet:
                    found=False
                    if not(found) and XorIDX<XorParamSet.count() :
                        if bp.name == XorParamSet[XorIDX].name :
                            found=True
                            p=XorParamSet[XorIDX]
                            XorIDX+=1
                            ptype="XOR"
                    if not(found) and OrIDX<OrParamSet.count() :
                        if bp.name == OrParamSet[OrIDX].name :
                            found=True
                            p=OrParamSet[OrIDX]
                            OrIDX+=1
                            ptype="OR"
                    if not(found) and KeyBoardIDX<KeyBoardParamSet.count() :
                        if bp.name == KeyBoardParamSet[KeyBoardIDX].name :
                            found=True
                            p=KeyBoardParamSet[KeyBoardIDX]
                            KeyBoardIDX+=1
                            ptype="KeyBoard"
                    assert found, "Found must be true at this point"
                    row=ET.SubElement(table,'tr')
                    if con.constraint!='' :
                        ET.SubElement(row,'td').text=pg.name+':['+con.constraint+']'+p.name
                    else :
                        ET.SubElement(row,'td').text=pg.name+':'+p.name
                    '''definition'''
                    ET.SubElement(row,'td').text=p.definition
                    '''value'''
                    if ptype=='XOR' :
                        ET.SubElement(row,'td').text='One value from list'
                    elif ptype=='OR' :
                        ET.SubElement(row,'td').text='One or more values from list'
                    elif ptype=='KeyBoard' :
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
                    else :
                        assert False, "Unrecognised type"

                    if ptype=='XOR' or ptype=='OR' :
                        ''' I should be constrained by vocab '''
                        assert p.vocab, 'I should have a vocabulary'
                        ''' find all values associated with this vocab '''
                        # all values that are part of this vocab
                        valset=Term.objects.filter(vocab=p.vocab)
                        vocabValues=""
                        counter=0
                        for v in valset:
                            '''name'''
                            counter+=1
                            vocabValues+=v.name
                            if counter != len(valset) :
                                vocabValues+=", "
                        ET.SubElement(row,'td').text=vocabValues
                    elif ptype=='KeyBoard':
                        ET.SubElement(row,'td').text='n/a'
                    else :
                        assert False, "Unrecognised type"

                    values=''
                    if ptype=='KeyBoard':
                        values=p.value
                    elif ptype=='XOR':
                        if p.value :
                            values=p.value.name
                    elif ptype=='OR':
                        if p.value :
                            valset=p.value.all()
                            counter=0
                            for value in valset :
                                counter+=1
                                values+=value.name
                                if counter != len(valset) :
                                    values+=", "
                    else:
                        assert False, "Unrecognised type"
                    ET.SubElement(row,'td').text=values

        return comp

    def cimRecord(self,rootElement) :
        ''' return the top level cim document invarient structure from within a CIMRecordSet'''
        cr1=ET.SubElement(rootElement,'CIMRecord')
        cr2=ET.SubElement(cr1,'CIMRecord')
        return cr2
    
    def cimRecordRoot(self):
        ''' return the top level cim document invarient structure '''
        root=ET.Element('CIMRecord', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        return root

    def cimRecordSetRoot(self):
        ''' return the top level cim document invarient structure for a recordset'''
        root=ET.Element('CIMRecordSet', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        return root

    def q2cim(self,ref,docType):

        ''' primary public entry point. '''
        method_name = 'add_' + str(docType)
        logging.debug("q2cim calling "+method_name)
        method = getattr(self, method_name)
        # make a special case for simulation as we output
        # all information associated with a simulation
        # using a CIMRecordSet
        if method_name=='add_simulation' :
            # save our simulation instance so the composition can pick it up
            self.simClass=ref
            root=self.cimRecordSetRoot()
            modelElement=self.cimRecord(root)
            self.add_component(ref.numericalModel,modelElement)
            simulationElement=self.cimRecord(root)
            self.add_simulation(ref,simulationElement)
            if ref.ensembleMembers>1 :
                ensembleElement=self.cimRecord(root)
                self.add_ensemble(ref,ensembleElement)
            experimentElement=self.cimRecord(root)
            self.add_experiment(ref.experiment,experimentElement)
            platformElement=self.cimRecord(root)
            self.add_platform(ref.platform,platformElement)

            uniqueFileList=[]
            couplings=ref.numericalModel.couplings(simulation=self.simClass)
            for coupling in couplings :
                externalClosures=ExternalClosure.objects.filter(coupling=coupling)
                for externalClosure in externalClosures :
                    if externalClosure.targetFile not in uniqueFileList :
                        uniqueFileList.append(externalClosure.targetFile)
            for fileObject in uniqueFileList :
                dataObjectElement=self.cimRecord(root)
                self.add_dataobject(fileObject,dataObjectElement)

            # find all unique grid references in our model
            uniqueGridList=[]
            myModel=ref.numericalModel
            self.componentWalk(myModel,uniqueGridList)
            for gridObject in uniqueGridList :
                gridObjectElement=self.cimRecord(root)
                self.add_gridobject(gridObject,gridObjectElement)
            cimDoc=root
        else :
            root=self.cimRecordRoot()
            cimDoc=method(ref,root)
        return cimDoc
        
    def componentWalk(self,c,uniqueGridList) :
        if c.implemented :
            if c.grid :
                if c.grid not in uniqueGridList :
                    uniqueGridList.append(c.grid)
            for child in c.components.all():
                self.componentWalk(child,uniqueGridList)

    def add_gridobject(self,gridObject,rootElement) :

        # temporary change to grid parent before Gerry fixes the questionnaire - will remove this section in time, but keeping it for now.
        #childGridList=gridObject.grids.all()
        #assert len(childGridList)==1, "expecting top level grid to have one child. Perhaps Gerry has fixed the issue with the extra grid level in the Questionnaire?"
        #gridObject=childGridList[0]
        # end temporary change to grid parent

        # get our horizontal and vertical grid properties
        # **** Assume they are in this order ****
        # We therefore need to constrain the order in which we load
        # these objects and also rely on them being stored in this
        # order as well.
        childList=gridObject.grids.all().order_by('id')
        assert len(childList)==2, "expecting 2 grid subcomponents (horizontal and vertical properties) but found "+len(childList)
        horizontalPropertiesObject=childList[0]
        verticalPropertiesObject=childList[1]

        HorizGridDiscretization=""
        HorizGridType=""
        HorizResProps={}
        # extract our horizontal properties
        for pg in horizontalPropertiesObject.paramGroup.all():
            #if pg.name :
            #    ET.SubElement(esmModelGridElement,"PROPERTIES",{"name":pg.name})
            if pg.name=="HorizontalCoordinateSystem" :
                # We rely on the constraint set objects appearing in our list in the same order as they appear in the questionnaire. We rely on this as the information we gather from this affects what we need to read from the others. The order_by('id') should sort this out but I've put a check in the code (for the first constraint only) just in case.
                first=True
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
                for con in constraintSet:
                    assert (con.constraint=="" and first) or (con.constraint!="" and not(first)), "Error, the first constraint set should have no associated constraint and there should only be one constraint set with no constraint"
                    #rootElement.append(ET.Comment('constraint : '+con.constraint))
                    BaseParamSet=BaseParam.objects.filter(constraint=con)
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if con.constraint=="" :
                            first=False
                            # first set of values have no constraint
                            if bp.name=="GridDiscretization" :
                                if p.value!="None" :
                                    HorizGridDiscretization=str(p.value)
                                else :
                                    HorizGridDiscretization=""
                            elif bp.name=="GridResolution" :
                                HorizGridResolution=str(p.value)
                            elif bp.name=="GridRefinementScheme" :
                                HorizGridRefinement=str(p.value)
                        elif HorizGridDiscretization!="" and str(con.constraint).find(HorizGridDiscretization)!=-1 and str(con.constraint).find("GridDiscretization")!=-1 :
                            #rootElement.append(ET.Comment('DEBUG: constraint : '+con.constraint))
                            #rootElement.append(ET.Comment('DEBUG: HorizGridDiscretization : '+HorizGridDiscretization))
                            #rootElement.append(ET.Comment('DEBUG: GridType : '+str(p.value)))
                            #rootElement.append(ET.Comment('DEBUG: PropertyName : '+str(bp.name)))
                            if bp.name=="GridType" :
                                HorizGridType=str(p.value)
                            elif bp.name=="CompositeGridDiscretization" :
                                #rootElement.append(ET.Comment('DEBUG: Getting names'))
                                HorizGridChildNames=[]
                                for term in p.value.all() :
                                    #rootElement.append(ET.Comment('DEBUG: Found name '+term.name))
                                    HorizGridChildNames.append(term.name)
                            elif bp.name=="CompositeGrid" :
                                HorizGridCompositeName=str(p.value)
                            else :
                                #rootElement.append(ET.Comment('ERROR: FOUND PROPERTY : '+str(bp.name)))
                                assert False, "Error : Unknown grid property found: "+bp.name
                        elif HorizGridType!="" and str(con.constraint).find(HorizGridType)!=-1 and str(con.constraint).find("GridType")!=-1 :
                            #rootElement.append(ET.Comment('DEBUG: Adding gridtype property : '+str(bp.name)+' '+str(p.value)))
                            HorizResProps[str(bp.name)]=str(p.value)
                        else :
                            # I am called if all the information has not been filled in.
                            pass
                            
            elif pg.name=="HorizontalExtent" :
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                for con in constraintSet:
                    #rootElement.append(ET.Comment('constraint : '+con.constraint))
                    BaseParamSet=BaseParam.objects.filter(constraint=con)
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if bp.name=="LatMin" :
                            HorizExtentLatMin=str(p.value)
                        elif bp.name=="LatMax" :
                            HorizExtentLatMax=str(p.value)
                        elif bp.name=="LonMin" :
                            HorizExtentLonMin=str(p.value)
                        elif bp.name=="LonMax" :
                            HorizExtentLonMax=str(p.value)
                        else :
                            assert False, "Error : Unknown grid extent property found: "+bp.name

        VertGridDiscretization=""
        VertGridType=""
        # extract our vertical properties
        for pg in verticalPropertiesObject.paramGroup.all():
            #if pg.name :
            #    ET.SubElement(esmModelGridElement,"PROPERTIES",{"name":pg.name})
            if pg.name=="VerticalCoordinateSystem" :
                # We rely on the constraint set objects appearing in our list in the same order as they appear in the questionnaire. We rely on this as the information we gather from this affects what we need to read from the others. The order_by('id') should sort this out but I've put a check in the code (for the first constraint only) just in case.
                first=True
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
                for con in constraintSet:
                    assert (con.constraint=="" and first) or (con.constraint!="" and not(first)), "Error, the first constraint set should have no associated constraint and there should only be one constraint set with no constraint"
                    #rootElement.append(ET.Comment('constraint : '+con.constraint))
                    BaseParamSet=BaseParam.objects.filter(constraint=con)
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if con.constraint=="" :
                            first=False
                            # first set of values have no constraint
                            if bp.name=="VerticalCoordinateType" :
                                VertGridDiscretization=str(p.value)
                        # rf need a better check below
                        elif str(con.constraint).find(VertGridDiscretization)!=-1 and str(con.constraint).find("GridDiscretization")!=-1:
                            #rootElement.append(ET.Comment('constraint : '+con.constraint))
                            #rootElement.append(ET.Comment('VertGridDiscretization : '+HorizGridDiscretization))
                            #rootElement.append(ET.Comment('GridType : '+str(p.value)))
                            if bp.name=="VerticalCoordinate" :
                                VertGridType=str(p.value)
                        else:
                            pass
        
        gridElement=ET.SubElement(rootElement,'gridSpec')
        esmModelGridElement=ET.SubElement(gridElement,'esmModelGrid',{'gridType':HorizGridType}) #,'verticalGridType':VertGridType})
        if gridObject.abbrev :
            ET.SubElement(esmModelGridElement,'shortName').text=gridObject.abbrev
        if gridObject.title :
            ET.SubElement(esmModelGridElement,'longName').text=gridObject.title
        if gridObject.description :
            ET.SubElement(esmModelGridElement,'description').text=gridObject.description
        #reference list TBA when Gerry adds in references
        #ET.SubElement(gridElement,'referenceList')

        if HorizGridDiscretization!="composite" :
            gridTileElement=ET.SubElement(esmModelGridElement,"gridTile",{"discretizationType":HorizGridDiscretization}) #,"verticalGridDiscretization":VertGridDiscretization})

            if horizontalPropertiesObject.abbrev :
                description=horizontalPropertiesObject.abbrev
            else :
                description=""
            ET.SubElement(gridTileElement,'shortName').text=description
            if horizontalPropertiesObject.title :
                ET.SubElement(gridTileElement,'longName').text=horizontalPropertiesObject.title
            if horizontalPropertiesObject.description :
                ET.SubElement(gridTileElement,'description').text=horizontalPropertiesObject.description

            horizResElement=ET.SubElement(gridTileElement,"horizontalResolution",{"details":HorizGridResolution})
            for attrib in HorizResProps.keys() :
                ET.SubElement(horizResElement,"property",{"name":attrib}).text=HorizResProps[attrib]
            horizResElement=ET.SubElement(gridTileElement,"horizontalExtent",{"LatMin":HorizExtentLatMin,"LatMax":HorizExtentLatMax,"LonMin":HorizExtentLonMin,"LonMax":HorizExtentLonMax})
            ET.SubElement(gridTileElement,"refinement").text=HorizGridRefinement
        elif HorizGridType=="ying yang":
            # ying yang is represented as a gridMosaic with two gridTiles
            gridMosaicElement=ET.SubElement(esmModelGridElement,"gridMosaic")
            ET.SubElement(gridMosaicElement,'shortName').text=HorizGridCompositeName
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
        elif HorizGridType=="icosahedral geodesic":
            gridMosaicElement=ET.SubElement(esmModelGridElement,"gridMosaic")
            # icosahedral geodesic is represented as a gridMosaic with ten gridTiles
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
            gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":HorizGridDiscretization})
        elif HorizGridType=="other":
            # we have a composite grid
            gridMosaicElement=ET.SubElement(esmModelGridElement,"gridMosaic")
            ET.SubElement(gridMosaicElement,"shortName").text=HorizGridCompositeName
            for gridTileName in HorizGridChildNames :
                gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":gridTileName})
        #else : output nothing

        self.addDocumentInfo(gridObject,gridElement)

    def add_ensemble(self,simClass,rootElement):

        ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
        assert(len(ensembleClassSet)==1,'Simulation %s should have one and only one associated ensembles class'%simClass)
        ensembleClass=ensembleClassSet[0]

        ensembleElement=ET.SubElement(rootElement,'ensemble')
        ''' responsibleParty [0..inf] '''
        self.addResp(simClass.centre.party,ensembleElement,'centre')
        ''' fundingSource [0..inf] '''
        ''' rationale [0..inf] '''
        ''' project [0->inf] '''
        ''' shortName [1] '''
        ET.SubElement(ensembleElement,'shortName').text=simClass.abbrev
        ''' longName [1] '''
        ET.SubElement(ensembleElement,'longName').text=simClass.title
        ''' description [0..1] '''
        ET.SubElement(ensembleElement,'description').text=ensembleClass.description
        ''' dataHolder [0..inf] '''
        ''' supports [1..inf] '''
        supportsElement=ET.SubElement(ensembleElement,'supports')
        self.addCIMReference(simClass.experiment,supportsElement)
        ''' output [0..inf] '''
        ''' ensembleType [1..inf] '''
        if ensembleClass.etype :
            self.addCVValue(ensembleElement,'ensembleType',ensembleClass.etype.name)
        ''' ensembleMember [2..inf] '''    
        ensMemberClassSet=EnsembleMember.objects.filter(ensemble=ensembleClass)
        assert(len(ensembleClassSet)>1,'Ensemble %s should have at least two ensemble members'%ensembleClass)
        for ensMemberClass in ensMemberClassSet :
            if ensMemberClass.drsMember :
                ensMemberElement=ET.SubElement(ensembleElement,'ensembleMember')
                simulationElement=ET.SubElement(ensMemberElement,'simulation')
                refElement=self.addCIMReference(simClass,simulationElement)
                if ensMemberClass.cmod :
                    self.addModelMod(ensMemberClass.cmod,refElement)
                if ensMemberClass.imod :
                    self.addInputMod(ensMemberClass.imod,refElement)
                #extIDElement=ET.SubElement(ensMemberElement,'externalID')
                #ET.SubElement(extIDElement,'name').text=ensMemberClass.drsMember
                #ET.SubElement(extIDElement,'standard',{'value':'DRS'})
                self.addCVValue(ensMemberElement,'externalID',ensMemberClass.drsMember,cvName='DRS_CMIP5_ensembleType')

        myEnsembleDoc=ensembleClass.makeDoc()
        self.addDocumentInfo(myEnsembleDoc,ensembleElement)
        
    def addModelMod(self,modClass,rootElement):
        changeElement=ET.SubElement(rootElement,"change",{'type':modClass.mtype.name})
        ET.SubElement(changeElement,'name').text=modClass.mnemonic
        if modClass.component :
            targetElement=ET.SubElement(changeElement,"changeTarget")
            # if we define a property (parameter) in this modification
            # and this property already exists in the associated
            # component then reference the property, otherwise reference
            # the component. Note, we do a case insensitive search.
            componentClass=modClass.component
            found=False
            for pg in componentClass.paramGroup.all() :
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                for con in constraintSet:
                    BaseParamSet=BaseParam.objects.filter(constraint=con)
                    for bp in BaseParamSet:
                        #ET.SubElement(targetElement,"DEBUG_PARAM_NAME").text=bp.name
                        # perform a case insensitive search
                        if bp.name.lower()==modClass.k.lower() :
                            found=True
                            break
                        if found : break
                    if found : break
                if found : break
            if found :
                self.addCIMReference(modClass.component,targetElement,argName=modClass.k,argType='componentProperty')
            else :
                self.addCIMReference(modClass.component,targetElement)

        detailElement=ET.SubElement(changeElement,'detail')
        if modClass.v :
            ET.SubElement(detailElement,'value').text=str(modClass.v)
        if modClass.k :
            ET.SubElement(detailElement,'name').text=modClass.k
        ET.SubElement(detailElement,'description').text=modClass.description

    def addInputMod(self,modClass,rootElement):
        changeElement=ET.SubElement(rootElement,"change",{'type':modClass.inputTypeModified.name})
        ET.SubElement(changeElement,'name').text=modClass.mnemonic
        if modClass.memberStartDate :
            changeElement.append(modClass.memberStartDate.xml('changeDate'))
        detailElement=ET.SubElement(changeElement,'detail')
        ET.SubElement(detailElement,'description').text=modClass.description

    def add_simulation(self,simClass,rootElement):

            #single simulation
            simElement=ET.SubElement(rootElement,'simulationRun')
            ''' responsibleParty [0..inf] '''
            self.addResp(simClass.contact,simElement,'contact')
            self.addResp(simClass.author,simElement,'author')
            self.addResp(simClass.funder,simElement,'funder')
            self.addResp(simClass.centre.party,simElement,'centre')
            ''' principleInvestigator [0..inf] '''
            ''' fundingSource [0..inf] '''
            ''' rationale [0..inf] '''
            if simClass.ensembleMembers>1 :
                # our simulation is really the base simulation of an ensemble
                ''' shortName [1] '''
                ET.SubElement(simElement,'shortName').text=simClass.abbrev+"BaseSimulation"
                ''' longName [1] '''
                ET.SubElement(simElement,'longName').text='Base Simulation of Ensemble'+simClass.title
            else :
                ''' shortName [1] '''
                ET.SubElement(simElement,'shortName').text=simClass.abbrev
                ''' longName [1] '''
                ET.SubElement(simElement,'longName').text=simClass.title
            ''' description [0..1] '''
            ET.SubElement(simElement,'description').text=simClass.description
            ''' supports [1..inf] '''
            experimentElement=ET.SubElement(simElement,'supports')
            self.addCIMReference(simClass.experiment,experimentElement)

            ''' calendar [1] '''
            if simClass.experiment.requiredCalendar :
                calendarElement=ET.SubElement(simElement,'calendar')
                ''' CIM choices : daily-360, realCalendar, perpetualPeriod '''
                calTypeElement=ET.SubElement(calendarElement,str(simClass.experiment.requiredCalendar.name))
            else :
                assert False, "Error, a calendar must exist"

            relatedSimulations=SimRelationship.objects.filter(sfrom=simClass)
            assert len(relatedSimulations)==1, "Expecting related simulations to be of size 1"
            relatedSimulation=relatedSimulations[0]
            if relatedSimulation.value :
                if str(relatedSimulation.value)=='usesSpinup':
                    #capture relationship as a spinup reference
                    spinupElement=ET.SubElement(simElement,'spinupSimulation')
                    self.addCIMReference(relatedSimulation.sto,spinupElement,description=relatedSimulation.description)
                elif str(relatedSimulation.value)=='hasControlSimulation':
                    #capture relationship as a control reference
                    controlElement=ET.SubElement(simElement,'controlSimulation')
                    self.addCIMReference(relatedSimulation.sto,controlElement,description=relatedSimulation.description)
                else:
                    # I am stored as a genealogy relationhip
                    pass
            ''' dataholder [0..inf] '''
            ''' conformance [0..inf] '''
            confClassSet=Conformance.objects.filter(simulation=simClass)
            for confClass in confClassSet:
                if (confClass.ctype) : # I have a conformance specified
                    if confClass.ctype.name=='Not Conformant' :
                        confElement=ET.SubElement(simElement,'conformance',{'conformant':'false'})
                    else :
                        confElement=ET.SubElement(simElement,'conformance',{'conformant':'true'})
                    reqElement=ET.SubElement(confElement,'requirement')
                    # get experiment class as the reference
                    ExperimentSet=Experiment.objects.filter(requirements=confClass.requirement)
                    assert len(ExperimentSet)==1, 'A requirement should have one and only one parent experiment.'
                    experiment=ExperimentSet[0]
                    assert confClass.requirement, 'There should be a requirement associated with a conformance'
                    self.addCIMReference(experiment,reqElement,argName=confClass.requirement.name,argType='NumericalRequirement')
                    # for each modelmod modification
                    for modClassBase in confClass.mod.all() :
                        modClass=modClassBase.get_child_object()
                        assert modClass._child_name=='codemod','Found a class type other than codemod'
                        sourceElement=ET.SubElement(confElement,'source')
                        if modClass._child_name=='codemod' :
                            # add a reference with the associated modification
                            self.addCIMReference(modClass.component,sourceElement,mod=modClass)
                        #    #elif im:
                        #    #    assert False, 'for some reason, modclass is never an input mod so I should not be called.'
                        #else:
                        #    assert False, 'modelmod must be an inputmod or a modelmod'  # error

                    # for each modelmod modification
                    # for some reason this is where we get the external couplings
                    for couplingClass in confClass.coupling.all():
                        sourceElement=ET.SubElement(confElement,'source')
                        assert couplingClass.targetInput, 'Error, couplingclass should have a targetinput'
                        self.addCIMReference(couplingClass.targetInput.owner,sourceElement,argName=couplingClass.targetInput.abbrev,argType="componentProperty")

                    #ET.SubElement(confElement,'description').text='Conformance type: "'+confClass.ctype.name+'". Notes: "'+confClass.description+'".'
                    confElement.append(ET.Comment('Conformance type : '+confClass.ctype.name))
                    ET.SubElement(confElement,'description').text=confClass.description

                elif (confClass.description and confClass.description!='') or len(confClass.mod.all())>0 or len(confClass.coupling.all())>0 :
                    # confClass.ctype is mot mandatory in the CIM but is required for a conformance so output something purely for validation purposes if other fields have been set without confClass.ctype being set
                    ET.SubElement(simElement,"conformance",{'type':'invalid'})
            ''' simulationComposite [0..1] '''
            # removed by Allyn in the latest version
            #''' ensemble [0..1] '''
            #if (simClass.ensembleMembers>1) :
            #    ensembleElement=ET.SubElement(simElement,'ensemble')
            #    ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
            #    assert(len(ensembleClassSet)==1,'Simulation %s should have one and only one associated ensembles class'%simClass)
            #    ensembleClass=ensembleClassSet[0]
            #    self.addCIMReference(ensembleClass,ensembleElement)
            ''' input [0..inf] ???COUPLING??? '''
            ''' output [0..inf] '''
            ''' restart [0..inf] '''
            ''' spinup [0..1] '''
            ''' deployment [0..1] '''
            dep2Element=ET.SubElement(simElement,'deployment')
            ET.SubElement(dep2Element,'description').text='The resources(deployment) on which this simulation ran'
            platElement=ET.SubElement(dep2Element,'platform')
            self.addCIMReference(simClass.platform,platElement)

            ''' previousSimulation [0..1] '''
            ''' simulationID [0..1] '''
            ''' startPoint [1] '''
            ET.SubElement(simElement,'startPoint').text=str(simClass.duration.startDate)
            ''' endPoint [0..1] '''
            if simClass.duration.endDate!=None:
                ET.SubElement(simElement,'endPoint').text=str(simClass.duration.endDate)
            ''' duration [0..1] '''
            if simClass.duration.length!=None:
                # we are using the standard schema duration type in the CIM here,
                # see http://www.w3schools.com/Schema/schema_dtypes_date.asp for
                # more details
                units={'Years':'Y','Days':'D'}
                durationElement=ET.SubElement(simElement,'duration',).text='P'+str(int(simClass.duration.length.period))+units[simClass.duration.length.units]
            ''' model [1] '''
            modelElement=ET.SubElement(simElement,'model')
            refElement=self.addCIMReference(simClass.numericalModel,modelElement)
            # now add in all mods associated with the simulation
            # to the reference
            for modelMod in simClass.codeMod.all() :
                self.addModelMod(modelMod,refElement)
            # input mods are not relevant here as they are included directly in the model description as composition information

            self.addDocumentInfo(simClass,simElement)

            ''' documentGenealogy [0..inf] '''
            #relatedSimulations=simClass.relatedSimulations.all()
            relatedSimulations=SimRelationship.objects.filter(sfrom=simClass)
            assert len(relatedSimulations)==1, "Expecting related simulations to be of size 1"
            relatedSimulation=relatedSimulations[0]
            if relatedSimulation.value :
                if str(relatedSimulation.value)=='usesSpinup':
                    #already captured the relationship as a spinup reference
                    pass
                elif str(relatedSimulation.value)=='hasControlSimulation':
                    #already captured the relationship as a control reference
                    pass
                else:
                    #capture relationship using the genealogy class
                    docGenElement=ET.SubElement(simElement,'documentGenealogy')
                    relationshipElement=ET.SubElement(docGenElement,'relationship')
                    # toTarget means that this relationship is about how I
                    # relate to the target
                    simRelationshipElement=ET.SubElement(relationshipElement,'simulationRelationship',{'type':str(relatedSimulation.value),'direction':'toTarget'})
                    ET.SubElement(simRelationshipElement,"description").text=relatedSimulation.description
                    targetElement=ET.SubElement(simRelationshipElement,"target")
                    self.addCIMReference(relatedSimulation.sto,targetElement)
            ''' quality [0..inf] '''
            if self.VALIDCIMONLY :
                simElement.append(ET.Comment('TBD: AuthorList: '+simClass.authorList))
            else :
                ET.SubElement(simElement,'Q_AuthorList').text=simClass.authorList

            return rootElement

    def addRequirement(self,reqClass,rootElement):
        if reqClass :
            reqElement=ET.SubElement(rootElement,'numericalRequirement')
            assert reqClass.ctype,"Error, requirement must have ctype set"
            mapping={'BoundaryCondition':'boundaryCondition','InitialCondition':'initialCondition','SpatioTemporalConstraint':'spatioTemporalConstraint'}
            typeElement=ET.SubElement(reqElement,mapping[reqClass.ctype.name])
            ''' numericalRequirement [0..inf] '''
            ''' id [0..1] '''
            ''' name [1] '''
            ET.SubElement(typeElement,'name').text=reqClass.name
            ''' description [0,1] '''
            ET.SubElement(typeElement,'description').text=reqClass.description
        
    def add_experiment(self,expClass,rootElement):

            expElement=ET.SubElement(rootElement,'numericalExperiment')
            ''' responsibleParty [0..inf] '''
            ''' principleInvestigator [0..inf] '''
            ''' fundingSource [0..inf] '''
            ''' rationale [1..inf] '''
            if expClass.rationale: 
                ET.SubElement(expElement,'rationale').text=expClass.rationale
            ''' measurementCampaign [0..inf] '''
            ''' requires [0..inf] '''
            ''' generates [0..inf] '''
            ''' duration [0..1] '''
            ''' supports [0..inf] '''
            ''' shortName [1] '''
            # short name is currently a concatenation of the experiment id
            # and the short name so separate these out
            expName,sep,expShortName=expClass.abbrev.partition(' ')
            assert sep!="", "Error, experiment short name does not conform to format 'id name'"
            if expShortName and expShortName!='' :
                ET.SubElement(expElement,'shortName').text=expShortName
            ''' longName [1] '''
            if expClass.title and expClass.title!='' :
                dummy1,dummy2,longName=expClass.title.partition(' ')
                assert dummy2!="", "Error, experiment long name does not conform to format 'id name'"
                ET.SubElement(expElement,'longName').text=longName
            ''' description [0..1] '''
            if expClass.description :
                ET.SubElement(expElement,'description').text=expClass.description
            ''' experimentNumber [0..1] '''
            if expName and expName!='' :
                ET.SubElement(expElement,'experimentNumber').text=expName
            ''' calendar [1] '''
            if expClass.requiredCalendar :
                calendarElement=ET.SubElement(expElement,'calendar')
                calTypeElement=ET.SubElement(calendarElement,str(expClass.requiredCalendar.name))
            else :
                assert False, "Error, a calendar must exist"
            ''' requiredDuration [1] '''
            # extract this information from the conformance?
            ET.SubElement(expElement,'requiredDuration')
            ''' numericalRequirement [1..inf] '''
            for reqClass in expClass.requirements.all():
                self.addRequirement(reqClass,expElement)

            self.addDocumentInfo(expClass,expElement)
            ''' documentGenealogy [0..inf] '''
            ''' quality [0..inf] '''

    def setComponentOptions(self,recurse,composition):

        self.recurse=recurse
        self.outputComposition=composition
    
    def add_component(self,compClass,rootElement):

        assert(compClass)
        if compClass :
            self.addChildComponent(compClass,rootElement,1,self.recurse)
        return rootElement

    def add_platform(self,platClass,rootElement):

        if platClass :
            platformElement=ET.SubElement(rootElement,'platform')
            if platClass.compiler :
                shortName=platClass.abbrev+platClass.compiler.name
                longName="Machine "+platClass.abbrev+" and compiler "+platClass.compiler.name
            else :
                shortName=platClass.abbrev+"CompilerUnspecified"
                longName="Machine "+platClass.abbrev+" and an unspecified compiler"

            ''' shortName [1] '''
            ET.SubElement(platformElement,'shortName').text=shortName
            ''' longName [0..1]'''
            ET.SubElement(platformElement,'longName').text=longName
            ''' description [0..1]'''
            if platClass.description :
                ET.SubElement(platformElement,'description').text=platClass.description
            ''' contact [0..inf] '''
            self.addResp(platClass.contact,platformElement,'contact','contact')
            ''' unit [1..inf] '''
            unitElement=ET.SubElement(platformElement,'unit')
            '''   machine '''
            machineElement=ET.SubElement(unitElement,'machine')
            '''     machineName [1] '''
            ET.SubElement(machineElement,'machineName').text=platClass.abbrev
            '''     machineSystem '''
            if platClass.hardware:
                ET.SubElement(machineElement,'machineSystem').text=platClass.hardware.name
            '''     machineLibrary '''
            '''     machineDescription '''
            '''     machineLocation '''
            '''     machineOperatingSystem '''
            if platClass.operatingSystem :
                self.addCVValue(machineElement,'machineOperatingSystem',platClass.operatingSystem.name)
            '''     machineVendor '''
            if platClass.vendor :
                self.addCVValue(machineElement,'machineVendor',platClass.vendor.name)
            '''     machineInterconnect '''
            if platClass.interconnect :
                self.addCVValue(machineElement,'machineInterconnect',platClass.interconnect.name)
            '''     machineMaximumProcessors '''
            if platClass.maxProcessors :
                ET.SubElement(machineElement,'machineMaximumProcessors').text=str(platClass.maxProcessors)
            '''     machineCoresPerProcessor '''
            if platClass.coresPerProcessor :
                ET.SubElement(machineElement,'machineCoresPerProcessor').text=str(platClass.coresPerProcessor)
            '''     machineProcessorType '''
            if platClass.processor :
                self.addCVValue(machineElement,'machineProcessorType',platClass.processor.name)
            '''   compiler '''
            compilerElement=ET.SubElement(unitElement,'compiler')
            '''     compilerName '''
            # mandatory in the CIM
            if platClass.compiler :
                ET.SubElement(compilerElement,'compilerName').text=platClass.compiler.name
            else :
                ET.SubElement(compilerElement,'compilerName').text='unspecified'
            '''     compilerVersion '''
            if platClass.compilerVersion :
                ET.SubElement(compilerElement,'compilerVersion').text=platClass.compilerVersion
            else :
               ET.SubElement(compilerElement,'compilerVersion').text='unspecified' 
            '''     compilerLanguage '''
            '''     compilerOptions '''
            '''     compilerEnvironmentVariables '''

            self.addDocumentInfo(platClass,platformElement)
            ''' documentGenealogy [0] '''
            ''' quality [0..inf] '''
        return rootElement

    def addCVValue(self,root,elementName,value,controlled=True,cvName='',cvURL='http://proj.badc.rl.ac.uk/svn/metafor/cmip5q/branches/vn1.0_devel',isOpen=True):
        if cvName=='' : cvName=elementName

        if controlled :
          type=ET.SubElement(root,elementName,{'value':value,'cv':'true'})
        else :
          type=ET.SubElement(root,'type',{'value':'Other','cv':'true'})
        open='false'
        if isOpen : open='true'
        #vocabServ=ET.SubElement(type,'controlledVocabulary',{'open':open})
        vocabServ=ET.SubElement(type,'controlledVocabulary')
        ET.SubElement(vocabServ,'name').text=cvName
        ET.SubElement(vocabServ,'server').text=cvURL
        if not controlled :
          type.text=value

    def addDocumentInfo(self,rootClass,rootElement) :
        try :
            ''' documentID [1] '''
            ET.SubElement(rootElement,'documentID').text=rootClass.uri
            ''' documentVersion [1] '''
            ET.SubElement(rootElement,'documentVersion').text=str(rootClass.documentVersion)
        except :
            #try :
            #    if (rootClass.doc) :
            #        ''' documentID [1] '''
            #        ET.SubElement(rootElement,'documentID').text=rootClass.doc.uri
            #        ''' documentVersion [1] '''
            #        ET.SubElement(rootElement,'documentVersion').text=str(rootClass.doc.documentVer#sion)
            #    else :
            #        ET.SubElement(rootElement,'documentID').text='[TBD]'
            #        ET.SubElement(rootElement,'documentVersion').text='[TBD]'
            #except :

            assert False, "Document is not of type Doc"
            #ET.SubElement(rootElement,'documentID').text='[TBD]'
            #ET.SubElement(rootElement,'documentVersion').text='[TBD]'

        ''' documentInternalVersion '''
        ''' metadataID '''
        ''' metadataVersion '''
        ''' documentAuthor [0..1] '''
        authorElement=ET.SubElement(rootElement,'documentAuthor')
        self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
        ''' documentCreationDate [1] '''
        ET.SubElement(rootElement,'documentCreationDate').text=datetime.datetime.isoformat(datetime.datetime.today())


    def constraintValid(self,con,constraintSet,root) :
        if con.constraint=='' : # there is no constraint
            return True
        else : # need to check the constraint
            # constraint format is : if <ParamName> [is|has] [not]* "<Value>"[ or "<Value>"]*
            #ET.SubElement(root,"DEBUG_Constraint").text=str(con.constraint)
            parsed=con.constraint.split()
            assert(parsed[0]=='if','Error in constraint format')
            assert(parsed[2]=='is' or parsed[2]=='has','Error in constraint format')
            paramName=parsed[1]
            #ET.SubElement(root,"DEBUG_Constraint_parameter").text=paramName
            if parsed[2]=='is' :
                singleValueExpected=True
            else:
                singleValueExpected=False
            #ET.SubElement(root,"DEBUG_Constraint_single_valued_parameter").text=str(singleValueExpected)
            if parsed[3]=='not' :
                negation=True
                idx=4
            else :
                negation=False
                idx=3
            #ET.SubElement(root,"DEBUG_Constraint_negation").text=str(negation)
            nValues=0
            valueArray=[]
            parsedQuote=con.constraint.split('"')
            #ET.SubElement(root,"DEBUG_Constraint_String_NSplit").text=str(len(parsedQuote))
            #for name in parsedQuote :
            #    ET.SubElement(root,"DEBUG_Constraint_String_Split").text=name
            idx2=2 # ignore the first load of text
            while idx2<len(parsedQuote) :
                #ET.SubElement(root,"DEBUG_Adding").text=parsedQuote[idx2-1]
                valueArray.append(parsedQuote[idx2-1])
                nValues+=1
                if (idx2+1)<len(parsedQuote) :
                    assert(parsed[idx2+1]=='or','Error in constraint format')
                idx2+=2
            assert(nValues>0)
            #ET.SubElement(root,"DEBUG_Constraint_nvalues").text=str(nValues)
            #for value in valueArray :
            #    ET.SubElement(root,"DEBUG_Constraint_value").text=value
            # now check if the constraint is valid or not
            # first find the value(s) of the parameter that is referenced
            found=False
            refValue=''
            for con in constraintSet:
                if not(found):
                    # see if it is a Xor
                    pset=XorParam.objects.filter(constraint=con)
                    for p in pset:
                        if (p.name==paramName) :
                            found=True
                            if p.value:
                                refValue=p.value.name
                    if not found:
                        # see if it is an or
                        pset=OrParam.objects.filter(constraint=con)
                        for p in pset:
                            if (p.name==paramName) :
                                found=True
                                if p.value:
                                    valset=p.value.all()
                                    counter=0
                                    for value in valset :
                                        counter+=1
                                        refValue+=value.name
                                        if counter != len(valset) :
                                            refValue+=", "
                    if not found:
                        # see if it is a keyboard value
                        pset=KeyBoardParam.objects.filter(constraint=con)
                        for p in pset:
                            if (p.name==paramName) :
                                found=True
                                refValue=p.value
            assert found,'Error, can not find property that is referenced by constraint'
            #ET.SubElement(root,"DEBUG_Constraint_refvalues").text=refValue
            if refValue=='' : # the reference parameter does not have any values set
                return True # output constraint parameters if the reference parameter is not set. This is an arbitrary decision, I could have chosen not to.
            match=False
            for value in refValue.split(','):
                if not(match) :
                    stripSpaceValue=value.strip()
                    if stripSpaceValue != '' :
                        if stripSpaceValue in valueArray :
                            match=True
            #ET.SubElement(root,"DEBUG_Constraint_match").text=str(match)
            if negation :
                match=not(match)
            return match

    def addProperties(self,componentObject,rootElement):

        if componentObject.implemented :
            if componentObject.isParamGroup :
                # I am a parameter dressed as a component
                newRootElement=ET.SubElement(rootElement,'componentProperty',{'represented':'true'})
                '''shortName'''
                ET.SubElement(newRootElement,'shortName').text=componentObject.abbrev
                '''longName'''
                ET.SubElement(newRootElement,'longName').text=componentObject.title
                if componentObject.description :
                    ET.SubElement(newRootElement,'description').text=componentObject.description
            else :
                newRootElement=rootElement

            # add in any properties dressed as child components
            for childComponentObject in componentObject.components.all():
                if childComponentObject.isParamGroup and childComponentObject.implemented:
                    self.addProperties(childComponentObject,newRootElement)

            # add in properties associated with this component
            for pg in componentObject.paramGroup.all():
              componentProperty={}
              if pg.name=="General Attributes" or pg.name=="Attributes": # skip general attributes as this is just a container for grouping properties in the Questionnaire. The Attributes test is due to "top level" components using this for some reason. I've created a ticket (716) for this.
                componentProperty=newRootElement
              else:
                componentProperty=ET.SubElement(newRootElement,'componentProperty',{'represented':'true'})

                '''shortName'''
                ET.SubElement(componentProperty,'shortName').text=pg.name
                '''longName'''
                ET.SubElement(componentProperty,'longName').text=pg.name

              # the internal questionnaire representation is that all parameters
              # are contained in a constraint group
              constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
              for con in constraintSet:
                if con.constraint!='' :
                    componentProperty.append(ET.Comment('Constraint start: '+con.constraint))
                if not(self.constraintValid(con,constraintSet,componentProperty)) :
                    componentProperty.append(ET.Comment('Constraint is invalid'))
                else :
                    #
                    # Needed to add .order_by('id') as the database does not guarantee
                    # to return objects in the same order, hence the order of the baseclass
                    # objects might not be the same as the Xor, Or, or KeyBoard objects
                    # whereas the code assumes the same order.
                    #
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    XorParamSet=XorParam.objects.filter(constraint=con).order_by('id')
                    OrParamSet=OrParam.objects.filter(constraint=con).order_by('id')
                    KeyBoardParamSet=KeyBoardParam.objects.filter(constraint=con).order_by('id')
                    XorIDX=0
                    OrIDX=0
                    KeyBoardIDX=0
                    for bp in BaseParamSet:
                        found=False
                        if not(found) and XorIDX<XorParamSet.count() :
                            if bp.name == XorParamSet[XorIDX].name :
                                found=True
                                p=XorParamSet[XorIDX]
                                XorIDX+=1
                                ptype="XOR"
                        if not(found) and OrIDX<OrParamSet.count() :
                            if bp.name == OrParamSet[OrIDX].name :
                                found=True
                                p=OrParamSet[OrIDX]
                                OrIDX+=1
                                ptype="OR"
                        if not(found) and KeyBoardIDX<KeyBoardParamSet.count() :
                            if bp.name == KeyBoardParamSet[KeyBoardIDX].name :
                                found=True
                                p=KeyBoardParamSet[KeyBoardIDX]
                                KeyBoardIDX+=1
                                ptype="KeyBoard"
                        assert found, "Found must be true at this point"

                        # skip CV output if the value is "n/a" for XOR or OR and if (for OR) there is only one value chosen. The validation step will flag the existence of N/A with other values
                        if (ptype=='XOR' and p.value and p.value.name=='N/A') :
                            componentProperty.append(ET.Comment('Value of XOR property called '+p.name+' is N/A so skipping'))
                        elif (ptype=='OR' and p.value and len(p.value.all())==1 and ('N/A' in str(p.value.all()))) : # last clause is messy as we turn the value into a string in a nasty way but I don't know how to do it another way
                            componentProperty.append(ET.Comment('Value of OR property called '+p.name+' is N/A so skipping'))
                        else :
                            property=ET.SubElement(componentProperty,'componentProperty',{'represented': 'true'})
                            '''shortName'''
                            ET.SubElement(property,'shortName').text=p.name
                            '''longName'''
                            ET.SubElement(property,'longName').text=p.name
                            '''description'''
                            '''value'''
                            if ptype=='KeyBoard':
                                ET.SubElement(property,'value').text=p.value
                            elif ptype=='XOR':
                                value=''
                                if p.value:
                                    value=p.value.name
                                ET.SubElement(property,'value').text=value
                            elif ptype=='OR':
                                if p.value :
                                    valset=p.value.all()
                                    for value in valset :
                                        ET.SubElement(property,'value').text=value.name
                if con.constraint!='' :
                    componentProperty.append(ET.Comment('Constraint end: '+con.constraint))

    def addChildComponent(self,c,root,nest,recurse=True):

      if c.implemented or nest==1:
        comp=ET.SubElement(root,'modelComponent')
        '''shortName'''
        ET.SubElement(comp,'shortName').text=c.abbrev
        '''longName'''
        ET.SubElement(comp,'longName').text=c.title
        '''description'''
        ET.SubElement(comp,'description').text=c.description
        '''license'''
        '''componentProperties'''
        componentProperties=ET.SubElement(comp,'componentProperties')
        self.addProperties(c,componentProperties)

        # Add any coupling inputs that have been defined for this component
        Inputs=ComponentInput.objects.filter(owner=c)
        for CompInpClass in Inputs :
            cp=ET.SubElement(componentProperties,'componentProperty',{'represented':'true'})
            '''shortName'''
            ET.SubElement(cp,'shortName').text=CompInpClass.abbrev
            '''longName'''
            ET.SubElement(cp,'longName').text=CompInpClass.abbrev
            '''description'''
            if CompInpClass.description :
                ET.SubElement(cp,'description').text=CompInpClass.description
            '''units'''
            if CompInpClass.units :
                ET.SubElement(cp,'units',{'value' : CompInpClass.units})
            '''cfname'''
            if CompInpClass.cfname :
                ET.SubElement(cp,'cfName').text=CompInpClass.cfname.name
        '''numericalProperties'''
        ET.SubElement(comp,'numericalProperties')
        '''scientificProperties'''
        ET.SubElement(comp,'scientificProperties')
        '''grid'''
        '''responsibleParty [0..inf]'''
        self.addResp(c.author,comp,'PI')
        self.addResp(c.funder,comp,'funder')
        self.addResp(c.contact,comp,'contact')
        self.addResp(c.centre.party,comp,'centre')
        '''releaseDate [0..1] type:dateTime'''
        if c.yearReleased :
            ET.SubElement(comp,'releaseDate').text=str(c.yearReleased)
        '''fundingSource'''
        '''citation'''
        self.addReferences(c.references,comp)
        '''composition'''
        self.addComposition(c,comp)
        if recurse:
            '''childComponent'''
            for child in c.components.all():
                if child.isParamGroup:
                    # skip as I am a parameter dressed as a component
                    pass
                elif child.implemented:
                    comp2=ET.SubElement(comp,'childComponent')
                    self.addChildComponent(child,comp2,nest+1)
                else : # child is not implemented
                    comp.append(ET.Comment('Component '+child.abbrev+' has implemented set to false'))
        '''parentComponent'''
        '''deployment'''
        '''activity'''
        '''type'''
        # always output the metafor sciencetype
        self.addCVValue(comp,'type',c.scienceType,controlled=c.controlled,cvName='metafor')
        # if it is a realm type then output the relevant drs realm type as well
        mapping={'Atmosphere':'atmos','Ocean':'ocean','LandSurface':'land','LandIce':'landIce','SeaIce':'seaIce','OceanBiogeoChemistry':'ocnBgchem','AtmosphericChemistry':'atmosChem','Aerosols':'aerosol'}
        if c.scienceType in mapping :
            self.addCVValue(comp,'type',mapping[c.scienceType],cvName='DRS_CMIP5_componentType',isOpen=False)
        '''component timestep info not explicitely supplied in questionnaire'''
        self.addDocumentInfo(c,comp)
        '''documentGenealogy [0..1] '''
        if c.otherVersion or c.geneology :
            GenEl=ET.SubElement(comp,'documentGenealogy')
            RelEl=ET.SubElement(GenEl,'relationship')
            DocEl=ET.SubElement(RelEl,'documentRelationship',{'type' : 'previousVersion'})
            if c.geneology :
                ET.SubElement(DocEl,'description').text=c.geneology
            TargEl=ET.SubElement(DocEl,'target')
            RefEl=ET.SubElement(TargEl,'reference')
            if c.otherVersion :
                ET.SubElement(RefEl,'name').text=c.otherVersion
        '''quality [0..inf] '''
      else:
          root.append(ET.Comment('Component '+c.abbrev+' has implemented set to false'))
        #logging.debug("component "+c.abbrev+" has implemented set to false")
      return

    def addReferences(self,references,rootElement):
        for ref in references.all():
            self.addReference(ref,rootElement)

    def addReference(self,refInstance,rootElement):
        if refInstance :
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


    def addSimpleResp(self,respName,rootElement,respType) :
        ciresp=ET.SubElement(rootElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
        ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respName
        role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')
        ET.SubElement(role,self.GMD_NAMESPACE_BRACKETS+'CI_RoleCode',{'codeList':'', 'codeListValue':respType})


    def addResp(self,respClass,rootElement,respType,parentElement='responsibleParty'):
        if (respClass) :
                if respClass.name == 'Unknown' : # skip the default respobject
                    rootElement.append(ET.Comment('responsibleParty '+respType+ ' is set to unknown. No CIM output will be generated.'))
                    return
                respElement=ET.SubElement(rootElement,parentElement)
                respElement.append(ET.Comment('responsibleParty uri :: '+respClass.uri))
                ciresp=ET.SubElement(respElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        #name=ET.SubElement(resp,'gmd:individualName')
        #ET.SubElement(name,'gco:CharacterString').text=c.contact
                if respClass.isOrganisation :
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'organisationName')
                else :
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
                ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.name
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
                if respClass.abbrev :
                    ET.SubElement(respElement,'abbreviation').text=respClass.abbrev

    def addComposition(self,c,comp):
        # couplings are all at the esm (root component) level
        couplings=[]
        if c.isModel:
            couplings=c.couplings(simulation=self.simClass)
        # see if I have any couplings. For some reason we can have couplings
        # without internal or external closures so need to check for closures
        coupled=False
        if len(couplings)>0 :
            for coupling in couplings :
                extclosures=ExternalClosure.objects.filter(coupling=coupling)
                if len(extclosures)>0 :
                    coupled=True
                intclosures=InternalClosure.objects.filter(coupling=coupling)
                if len(intclosures)>0 :
                    coupled=True
        if coupled :
            if self.outputComposition :
                composeElement=ET.SubElement(comp,'composition')
                for coupling in couplings:
                    # output each link separately as the questionnaire keeps information
                    # about transformations on a link by link basis
                    extclosures=ExternalClosure.objects.filter(coupling=coupling)
                    for closure in extclosures :
                        self.addCoupling(coupling,closure,composeElement,comp)
                    intclosures=InternalClosure.objects.filter(coupling=coupling)
                    for closure in intclosures :
                        self.addCoupling(coupling,closure,composeElement,comp)
                ET.SubElement(composeElement,'description').text='Coupling details for component '+c.abbrev
            else :
                comp.append(ET.Comment('Coupling information exists but its output has been switched off for this CIM Object'))

    def addCoupling(self,coupling,closure,composeElement,componentElement) :
        CompInpClass=coupling.targetInput
        assert CompInpClass,'A Coupling instance must have an associated ComponentInput instance'
        assert CompInpClass.owner,'A Coupling instance must have an associated ComponentInput instance with a valid owner'
        assert CompInpClass.ctype,'A Coupling instance must have an associated ctype value'
        couplingType=CompInpClass.ctype.name
        if couplingType=='BoundaryCondition' :
            couplingType='boundaryCondition'
        elif couplingType=='AncillaryFile' :
            couplingType='ancillaryFile'
        elif couplingType=='InitialCondition' :
            couplingType='initialCondition'
        couplingFramework=''
        # fully specified is true if we are referencing data in a file, otherwise it is not fully specified (as we are either referencing a file or a component)
        if closure.ctype=='external' and closure.target :
            couplingElement=ET.SubElement(composeElement,'coupling',{'purpose':couplingType,'fullySpecified':'true'})
        else :
            couplingElement=ET.SubElement(composeElement,'coupling',{'purpose':couplingType,'fullySpecified':'false'})
        '''description'''
        ET.SubElement(couplingElement,'description').text=coupling.manipulation
        '''type [0..1] '''
        if coupling.inputTechnique and couplingType=='boundaryCondition' :
            if coupling.inputTechnique.name!='' :
                ET.SubElement(couplingElement,'type',{'value':coupling.inputTechnique.name})
        '''timeProfile'''
        units=''
        if coupling.FreqUnits :
            units=str(coupling.FreqUnits.name)
        if units!='' or coupling.couplingFreq!=None :
            tpElement=ET.SubElement(couplingElement,'timeProfile',{'units':units})
            #ET.SubElement(tpElement,'start')
            #ET.SubElement(tpElement,'end')
            ET.SubElement(tpElement,'rate').text=str(coupling.couplingFreq)
        '''timeLag'''
        '''spatialRegridding'''
        if closure.spatialRegrid :
            regridValue=closure.spatialRegrid.name
            if regridValue=='Conservative' :
                sr=ET.SubElement(couplingElement,'spatialRegridding',{'conservativeSpatialRegridding':'true'})
                ET.SubElement(sr,'spatialRegriddingOrder').text='TBD'
            elif regridValue=='Non-Conservative' :
                sr=ET.SubElement(couplingElement,'spatialRegridding',{'conservativeSpatialRegridding':'false'})
                ET.SubElement(sr,'spatialRegriddingOrder').text='TBD'
            # else do nothing as the value is 'None'
        '''timeTransformation'''
        if closure.temporalTransform :
            tt=ET.SubElement(couplingElement,'timeTransformation')
            ET.SubElement(tt,'mappingType',{'value': closure.temporalTransform.name})
        '''couplingSource'''
        sourceElement=ET.SubElement(couplingElement,'couplingSource')
        if closure.ctype=='internal' and closure.target :
            # reference to component
            self.addCIMReference(closure.target,sourceElement)
        elif closure.ctype=='external' and closure.target :
            # reference to a field in a file
            # we reference the file here and the field in the "connection"
            self.addCIMReference(closure.targetFile,sourceElement)
        elif closure.ctype=='external' and closure.targetFile :
            # reference directly to a file
            self.addCIMReference(closure.targetFile,sourceElement)
        else :
            sourceElement.append(ET.Comment('error: couplingSource closure has no target and (for ExternalClosures) no targetFile'))

        '''couplingTarget'''          
        targetElement=ET.SubElement(couplingElement,'couplingTarget')
        self.addCIMReference(CompInpClass.owner,targetElement)
        '''priming'''
        '''connection'''
        connectionElement=ET.SubElement(couplingElement,'connection')
        if closure.ctype=='external' and closure.target :
            # we are referencing data in a file
            sourceElement=ET.SubElement(connectionElement,'connectionSource')
            self.addCIMReference(closure.targetFile,sourceElement,argName=closure.target.variable,argType='fileVariable')
        else :
            connectionElement.append(ET.Comment('this coupling has no connection source specified'))
        # we know that we always have a connectionTarget as we create it
        # we know that we never have a connectionSource as there is no such concept in the Questionnaire
        targetElement=ET.SubElement(connectionElement,'connectionTarget')
        self.addCIMReference(CompInpClass.owner,targetElement,argName=CompInpClass.abbrev,argType='componentProperty')


    def addCIMReference(self,rootClass,rootElement,argName='',argType='',mod=None, description=''):

        if argName!='' :
            assert argType!='', 'If argName is specified then argType must also be specified'
        if argType!='' :
            assert argName!='', 'If argType is specified then argName must also be specified'
        try :
            myURI=rootClass.uri
            myDocumentVersion=rootClass.documentVersion
            myName=rootClass.abbrev
            myType=rootClass._meta.module_name
            if myType=='datacontainer' :
                 myType='dataObject'
                 # hack as pre-loaded files do not have an abbreviation
                 if myName=='' :
                     myName=rootClass.title
            elif myType=='component' :
                myType='modelComponent'

        except :
            # temporary hack before we make the ensemble class a doc
            assert False, "Document is not of type Doc"
            #myURI="[TBD]"
            #myDocumentVersion="[TBD]"
            #myName="[TBD]"
            #myType="[TBD]"

        targetRef=ET.SubElement(rootElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':'#//CIMRecord/'+myType+'[id=\''+myURI+'\']'})
        ''' id '''
        ET.SubElement(targetRef,'id').text=myURI
        ''' name '''
        if argName!='' :
            ET.SubElement(targetRef,'name').text=argName
        else :
            ET.SubElement(targetRef,'name').text=myName
        ''' type '''
        if argType!='' :
            ET.SubElement(targetRef,'type').text=argType
        else :
            ET.SubElement(targetRef,'type').text=myType
        ''' version '''
        ET.SubElement(targetRef,'version').text=str(myDocumentVersion)
        ''' description '''
        if description!='' :
            ET.SubElement(targetRef,'description').text=description
        elif argType!='' and argName!='' :
            ET.SubElement(targetRef,'description').text='Reference to a '+argType+' called '+argName+' in a '+myType+' called '+myName
        else :
            ET.SubElement(targetRef,'description').text='Reference to a '+myType+' called '+myName
        if mod :
            modElement=ET.SubElement(targetRef,'change')
            ET.SubElement(modElement,'name').text=mod.mnemonic
            detailElement=ET.SubElement(modElement,'detail',{'type':mod.mtype.name})
            ET.SubElement(detailElement,'description').text=mod.description
        return targetRef

    def add_dataobject(self,fileClass,rootElement):

        if fileClass :
            doElement=ET.SubElement(rootElement,'dataObject',{'dataStatus':'complete'})
            ''' acronym [1]'''
            ET.SubElement(doElement,'acronym').text=fileClass.abbrev
            ''' description [0..1]'''
            if fileClass.description!='' :
                ET.SubElement(doElement,'description').text=fileClass.description
            ''' hierarchyLevelName [0..1]'''
            ''' hierarchyLevelValue [0..1]'''
            ''' keyword [0..1]'''
            ''' geometryModel [0..1]'''
            ''' restriction [0..inf]'''
            ''' storage [0..1]'''
            storeElement=ET.SubElement(doElement,'storage')
            lfElement=ET.SubElement(storeElement,'ipStorage')
            #ET.SubElement(lfElement,'dataSize').text='0'
            if fileClass.format :
                if fileClass.format.name=='Text' :
                    name='ASCII'
                else :
                    name=fileClass.format.name
                ET.SubElement(lfElement,'dataFormat',{'value':name})
            ''' protocol [0..1] '''
            #ET.SubElement(lfElement,'protocol')
            ''' host [0..1] '''
            #ET.SubElement(lfElement,'host')
            if fileClass.link :
                ET.SubElement(lfElement,'path').text=fileClass.link
            ''' fileName [1]'''
            ET.SubElement(lfElement,'fileName').text=fileClass.title
            ''' distribution [1] '''
            distElement=ET.SubElement(doElement,'distribution')
            if fileClass.format :
                if fileClass.format.name=='Text' :
                    name='ASCII'
                else :
                    name=fileClass.format.name
                ET.SubElement(distElement,'distributionFormat',{'value':name})
            ''' childObject [0..inf]'''
            ''' parentObject [0..1]'''
            ''' citation [0..inf]'''
            self.addReference(fileClass.reference,doElement)
            ''' content [0..inf]'''
            for variable in DataObject.objects.filter(container=fileClass) :
                contentElement=ET.SubElement(doElement,'content')
                ''' topic [1] '''
                topicElement=ET.SubElement(contentElement,'topic')
                '''    name [1] '''
                if variable.variable!='' :
                    ET.SubElement(topicElement,'name').text=variable.variable
                '''    standardName [0..1] '''
                if variable.cfname :
                    ET.SubElement(topicElement,'standardName',{'standard':'CF'}).text=variable.cfname.name
                '''    description [0..1] '''
                if variable.description :
                    ET.SubElement(topicElement,'description').text=variable.description
                '''    unit [0..1] '''
                ''' aggregation [1] '''
                ET.SubElement(contentElement,'aggregation')
                ''' frequency [1] '''
                ET.SubElement(contentElement,'frequency')
                ''' citation [0..inf] '''
                self.addReference(variable.reference,contentElement)
            ''' extent [0..1]'''
            ''' generic document elements '''
            self.addDocumentInfo(fileClass,doElement)
            ''' documentGenealogy [0..1] '''
            ''' quality [0..1] '''

    # the following methods are no longer used and have had XXX added to the start of them

    def XXXaddDataRef(self,dataObjectClass,rootElement):
        assert(dataObjectClass,'dataObject should not be null')
        assert(dataObjectClass.container,'dataContainer should not be null')
        dataRefElement=ET.SubElement(rootElement,"Q_DataRef")
        ET.SubElement(dataRefElement,"Q_VariableName").text=dataObjectClass.variable
        ET.SubElement(dataRefElement,"Q_FileName").text=dataObjectClass.container.name

    def XXXadd_datacontainer(self,dataContainerClass,rootElement):
        if dataContainerClass :
            dataContainerElement=ET.SubElement(rootElement,"Q_dataContainer")
            ET.SubElement(dataContainerElement,"Q_Name").text=dataContainerClass.title
            ET.SubElement(dataContainerElement,"Q_URL").text=dataContainerClass.link
            ET.SubElement(dataContainerElement,"Q_Description").text=dataContainerClass.description
            formatElement=ET.SubElement(dataContainerElement,'Q_FormatVal')
            self.addValue(dataContainerClass.format,formatElement)
            self.addReference(dataContainerClass.reference,dataContainerElement)
            # add any associated data
            dataObjectsElement=ET.SubElement(dataContainerElement,'Q_DataObjects')
            dataObjectInstanceSet=DataObject.objects.filter(container=dataContainerClass)
            logging.info('FIXME: Currently skipping XML conversion for data objects')
            #for dataObjectInstance in dataObjectInstanceSet:
            #    self.addDataObject(dataObjectInstance,dataObjectsElement)
        return rootElement

    def XXXaddDataObject(self,dataObjectClass,rootElement):
        assert(dataObjectClass,'dataObject should not be null')
        dataElement=ET.SubElement(rootElement,"Q_DataObject")
        ET.SubElement(dataElement,"Q_description").text=dataObjectClass.description
        ET.SubElement(dataElement,"Q_variable").text=dataObjectClass.variable
        ET.SubElement(dataElement,"Q_cfname").text=dataObjectClass.cftype
        self.addReference(dataObjectClass.reference,dataElement)
        # dataClass.featureType is unused at the moment
        # dataClass.drsAddress is unused at the moment

    def XXXaddEnsemble(self,ensembleClass,rootElement):

        if ensembleClass :
            ensembleElement=ET.SubElement(rootElement,'Q_Ensemble')
            ET.SubElement(ensembleElement,'Q_Description').text=ensembleClass.description
            etypeValueElement=ET.SubElement(ensembleElement,'Q_EtypeValue')
            self.addValue(ensembleClass.etype,etypeValueElement)
            ensMembersElement=ET.SubElement(ensembleElement,'Q_EnsembleMembers')
            ensMemberClassSet=EnsembleMember.objects.filter(ensemble=ensembleClass)
            for ensMemberClass in ensMemberClassSet :
                self.addEnsMember(ensMemberClass,ensMembersElement)

    def XXXaddEnsMember(self,ensMemberClass,rootElement):

        if ensMemberClass :
            ensMemberElement=ET.SubElement(rootElement,'Q_EnsembleMember')
            ET.SubElement(ensMemberElement,'Q_Number').text=str(ensMemberClass.memberNumber)
            # reference the modification here to avoid replication as it is stored as part of the simulation
            self.addModificationRef(ensMemberClass.mod,ensMemberElement)

    def XXXaddModificationRef(self,modClass,rootElement) :
        if modClass :
            modRefElement=ET.SubElement(rootElement,'Q_ModificationRef')
            modRefElement.append(ET.Comment("WARNING: Modification information still needs to be added."))

    def XXXaddModification(self,modClass,rootElement) :
        if modClass :
            modElement=ET.SubElement(rootElement,'Q_Modification')
            ET.SubElement(modElement,'Q_Mnemonic').text=modClass.mnemonic
            mtypeValueElement=ET.SubElement(modElement,'Q_MtypeValue')
            self.addValue(modClass.mtype,mtypeValueElement)
            ET.SubElement(modElement,'Q_Description').text=modClass.description

    def XXXaddModelMod(self,modelModClass,rootElement) :
        if modelModClass :
            modelModElement=ET.SubElement(rootElement,'Q_ModelMod')
            # ModelMod isa Modification
            self.addModification(modelModClass,modelModElement)
            if modelModClass.component :
                compElement=ET.SubElement(modelModElement,'Q_ComponentRef')
                ET.SubElement(compElement,'Q_ComponentName').text=modelModClass.component.abbrev

    def XXXaddInputMod(self,inputModClass,rootElement) :
        if inputModClass :
            inputModElement=ET.SubElement(rootElement,'Q_InputMod')
            # InputMod isa Modification
            self.addModification(inputModClass,inputModElement)
            ET.SubElement(inputModElement,'Q_Date').text=str(inputModClass.date)
            couplingsElement=ET.SubElement(inputModElement,'Q_Couplings')
            for couplingClass in inputModClass.inputs.all():
                self.addCouplingRef(couplingClass,couplingsElement)

    def XXXaddCouplingRef(self,couplingClass,rootElement):
        if couplingClass :
            couplingElement=ET.SubElement(rootElement,'Q_CouplingRef')
            if couplingClass.targetInput:
                if couplingClass.targetInput.owner:
                    ET.SubElement(couplingElement,'Q_ComponentName').text=couplingClass.targetInput.owner.abbrev
                if couplingClass.targetInput.realm:
                    ET.SubElement(couplingElement,'Q_RealmName').text=couplingClass.targetInput.realm.abbrev
                ET.SubElement(couplingElement,'Q_AttrName').text=couplingClass.targetInput.abbrev
                if couplingClass.targetInput.ctype:
                    ET.SubElement(couplingElement,'Q_Type').text=couplingClass.targetInput.ctype.name

    def XXXaddCentre(self,centreClass,rootElement):
        if centreClass :
            centreElement=ET.SubElement(rootElement,'Q_Centre')
            #centreClass is a ResponsibleParty
            self.addResp(centreClass.party,centreElement,'centre')

    def XXXaddVocab(self,vocabClass,rootElement):
        if vocabClass :
            vocabElement=ET.SubElement(rootElement,'Q_Vocab')
            ET.SubElement(vocabElement,'Q_Name').text=vocabClass.name
            ET.SubElement(vocabElement,'Q_URI').text=vocabClass.uri
            ET.SubElement(vocabElement,'Q_Note').text=vocabClass.note
            ET.SubElement(vocabElement,'Q_Version').text=vocabClass.version

    def XXXaddValue(self,valueClass,valueElement):
        if valueClass :
            ET.SubElement(valueElement,'Q_Value').text=valueClass.name
            self.addVocab(valueClass.vocab,valueElement)
            ET.SubElement(valueElement,'Q_Definition').text=valueClass.definition
            ET.SubElement(valueElement,'Q_Version').text=valueClass.version

    def XXXaddConformance(self,confClass,rootElement):
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

    def XXXaddComponentDoc(self,docClass,rootElement):

        if docClass :
            docElement=ET.SubElement(rootElement,'Q_Doc')
            self.addResp(docClass.metadataMaintainer,docElement,'metadataMaintainer')
            ET.SubElement(docElement,'Q_MetadataVersion').text=docClass.metadataVersion
            ET.SubElement(docElement,'Q_DocumentVersion').text=str(docClass.documentVersion)
            ET.SubElement(docElement,'Q_Created').text=str(docClass.created)
            ET.SubElement(docElement,'Q_Updated').text=str(docClass.updated)


    def XXXaddDoc(self,docClass,rootElement):

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
