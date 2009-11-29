import os,tempfile
from lxml import etree as ET
import logging
import pkg_resources

#http://peak.telecommunity.com/DevCenter/PkgResources#resourcemanager-api
XSLDIR=pkg_resources.resource_filename("cmip5q","xsl")  # TODO: do we need to worry about cleanup?
XSDDIR=pkg_resources.resource_filename("cmip5q","xsd")  # TODO: do we need to worry about cleanup?

def shellcommand(command):
    ''' lightweight wrapper to os.system that logs the return and handles errors '''
    logging.debug('Executing '+command)
    r=os.system(command)
    logging.debug(r)
    return r

def viewer(xml):
    ''' Rupert's xslt view, xml is an element tree instance '''
    # we need the xml in a temporary file
    tmpfname=tempfile.mktemp('.xml')
    tmpf=open(tmpfname,'w')
    tmpf.write(ET.tostring(xml))
    tmpf.close()
    # prettify the xml file with an xsl stylesheet
    outfname=tempfile.mktemp('.tmp')
    formatter=os.path.join(XSLDIR,'xmlformat.xsl')
    r=shellcommand('xsltproc %s %s > %s'%(formatter,tmpfname,outfname))
    r=shellcommand("mv %s %s"%(outfname,tmpfname))

    # create and return html rendered xml using an xsl stylesheet
    formatter=os.path.join(XSLDIR,'xmlverbatim.xsl')
    shellcommand('xsltproc %s %s > %s'%(formatter,tmpfname,outfname))

    # read html file
    outf=open(outfname, 'r')
    linestring=outf.read()
    outf.close()
    os.remove(outfname)
    return linestring

class Validator:
    ''' This is used to validate CIM documents '''
    def __init__(self,schemaValidate=False,contentValidate=True):
        ''' Setup validation tools etc '''
        self.XSLdir=XSLDIR
        self.XSDdir=XSDDIR
        self.CIMschema=os.path.join(self.XSDdir,'cim.xsd')
        self.schemaValidate=schemaValidate
        self.contentValidate=contentValidate
        self.nInvalid=0
        self.nChecks=0
        self.valid=True
        self.percentComplete=100.0
        self.cimHtml={}
        self.report={}

    def errorsAsHtml(self) :
        return self.report
    
    def xmlAsHtml(self) :
        return self.cimHtml
    
    def __validateComponent(self,CIMdoc):
        ''' Validation for a Component '''

        # perform any common validation
        report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,"CommonChecks.sch")
        self.report=report
        self.nChecks=nChecks
        self.nInvalid=nInvalid
        # perform any component specific validation
        report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,"ComponentChecks.sch")
        # add these results to the existing results
        reportRoot=self.report.getroot()
        reportRoot.append(report.getroot())
        self.nChecks+=nChecks
        self.nInvalid+=nInvalid
        # calculate any derived state
        self.__updateState()

    def __validateSimulation(self,CIMdoc):
        ''' Validation for a Simulation '''

        # perform any simulation specific validation
        report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,"SimulationChecks.sch")
        self.report=report
        self.nChecks=nChecks
        self.nInvalid=nInvalid
        # perform any common validation
        report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,"CommonChecks.sch")
        # add these results to the existing results
        reportRoot=self.report.getroot()
        reportRoot.append(report.getroot())
        self.nChecks+=nChecks
        self.nInvalid+=nInvalid
        # calculate any derived state
        self.__updateState()

    def __updateState(self):

        if self.nChecks>0:
            self.percentComplete=str(((self.nChecks-self.nInvalid)*100.0)/self.nChecks)
        else:
            self.percentComplete=100.0
        if self.nInvalid>0:
            self.valid=False
        else:
            self.valid=True

    def __CimAsHtml(self,CIMdoc):
        ''' generate the cim as html '''

        # first format it using xmlformat.xsl
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"xmlformat.xsl"))
        transform = ET.XSLT(xslt_doc)
        formattedCIMdoc = transform(CIMdoc)
        # next translate it into html using verbid.xsl
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"verbid.xsl"))
        transform = ET.XSLT(xslt_doc)
        cimHtml = transform(formattedCIMdoc)
        return cimHtml

    def __SchematronValidate(self,CIMdoc,SchematronFile,SchematronReport="schematron-report.xsl"):
        ''' Validation common to both Component and Simulation '''
        sct_doc = ET.parse(os.path.join(self.XSLdir,SchematronFile))
        #obtain schematron error report in html
        xslt_doc = ET.parse(os.path.join(self.XSLdir,SchematronReport))
        transform = ET.XSLT(xslt_doc)
        xslt_doc = transform(sct_doc)
        transform = ET.XSLT(xslt_doc)
        report = transform(CIMdoc)
        # find out how many errors and checks there were
        nChecks = len(report.xpath('//check'))
        nInvalid = len(report.xpath('//invalid'))
        return report,nChecks,nInvalid

    def validateFile(self,fileName):
        tmpDoc=ET.parse(file)
        self.validateDoc(tmpDoc)

    def validateDoc(self,CIMdoc,cimtype=''):
        ''' This method validates a CIM document '''
        #validate against schema
        if self.schemaValidate:
            #CIM currently fails the schema parsing
            xmlschema_doc = ET.parse(self.CIMschema)
            xmlschema = ET.XMLSchema(xmlschema_doc)
            if xmlschema.validate(CIMdoc):
                logging.debug("CIM Document validates against the cim schema")
            else:
                logging.debug("CIM Document fails to validate against the cim schema")
            log = xmlschema.error_log
            logging.debug("CIM Document schema errors are "+log)
            return log,

        if self.contentValidate:
            #validate against schematron checks
            if cimtype=='Component':
                self.__validateComponent(CIMdoc)
            elif cimtype=='Simulation':
                self.__validateSimulation(CIMdoc)
            else:
                raise ValueError('Invalid validation type found')

        # create an html representation of our document
        self.cimHtml=self.__CimAsHtml(CIMdoc)
