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

def viewer(xml,allModel=True):
    ''' Rupert's xslt view, xml is an element tree instance '''
    assert(allModel,True,'Support for not processing the entire model is not yet included')
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
       
    def __validateComponent(self,CIMdoc):
        ''' Validate a Component '''
        sct_doc = ET.parse(os.path.join(self.XSLdir,"BasicChecks.sch"))
        schematron = ET.Schematron(sct_doc)
        if schematron.validate(CIMdoc):
          logging.debug("CIM Document passes the schematron tests")
        else:
          logging.debug("CIM Document fails the schematron tests")

        #obtain schematron report in html
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"schematron-report.xsl"))
        transform = ET.XSLT(xslt_doc)
        xslt_doc = transform(sct_doc)
        transform = ET.XSLT(xslt_doc)
        schematronhtml = transform(CIMdoc)

        #also generate the cim as html
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"xmlformat.xsl"))
        transform = ET.XSLT(xslt_doc)
        formattedCIMdoc = transform(CIMdoc)
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"verbid.xsl"))
        transform = ET.XSLT(xslt_doc)
        cimhtml = transform(formattedCIMdoc)
        return schematronhtml,cimhtml
    
    
    def validate(self,CIMdoc,cimtype='component'):
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
            if cimtype=='component':
                return self.__validateComponent(CIMdoc)
      
       