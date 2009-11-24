
from protoq.models import *

from lxml import etree as ET
import uuid
import logging
import datetime


class Translator:

    ''' Translates a questionnaire Doc class (simulation, component or platform) into a CIM document (as an lxml etree instance) '''

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
        ''' I don't appear to have anything to do! '''

    def cimRoot(self):
        ''' return the top level cim document invarient structure '''
        root=ET.Element('CIMRecord', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        ET.SubElement(root,'id').text='[TBD1]'
        return root

    def q2cim(self,ref,docType):

        method_name = 'q2cim_' + str(docType)
        method = getattr(self, method_name)
        root=self.cimRoot()
        cimDoc=method(ref,root)
        return cimDoc
        
    def q2cim_simulation(self,ref,root):

        logging.debug('Translator:q2cim_simulation: returning an xml document')
        sim=ET.SubElement(root,'SIMULATION')
        return root

    def q2cim_component(self,ref,root):

        logging.debug('Translator:q2cim_component: returning an xml document')
        recurse=True
        self.addComponent(root,ref,1,recurse)
        return root

    def q2cim_platform(self,ref,root):

        logging.debug('Translator:q2cim_platform: returning an xml document')
        plat=ET.SubElement(root,'PLATFORM')
        return root

    def addComponent(self,root,c,nest,recurse=True):

      if c.implemented:
        if nest==1:
          # TBD documentVersion
          comp=ET.SubElement(root,'modelComponent',{'documentVersion': '-1', 'CIMVersion': '1.3'})
        else:
          comp=ET.SubElement(root,'modelComponent')
        '''composition'''
        self.composition(c,comp)
        if recurse:
            '''childComponent'''
            for child in c.components.all():
              if child.implemented:
                comp2=ET.SubElement(comp,'childComponent')
                self.addComponent(comp2,child,nest+1)
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

        self.addResp(resps,'author',c.author)
        self.addResp(resps,'funder',c.funder)
        self.addResp(resps,'contact',c.contact)
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

    def addResp(self,parent,respType,p):
        if (p) :
            resp=ET.SubElement(parent,"Q_responsibleParty",{'type':respType})
            ET.SubElement(resp,"Q_name").text=p.name
            ET.SubElement(resp,"Q_webpage").text=p.webpage
            ET.SubElement(resp,"Q_abbrev").text=p.abbrev
            ET.SubElement(resp,"Q_email").text=p.email
            ET.SubElement(resp,"Q_address").text=p.address
            ET.SubElement(resp,"Q_uri").text=p.uri
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

