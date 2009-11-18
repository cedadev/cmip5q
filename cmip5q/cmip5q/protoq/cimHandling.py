import os
from lxml import etree as ET
import logging

XSLDIR="xsl"  # TODO: we'll make this egg safe later
XSDDIR="xsd"  # TODO: We'll make this egg safe later

def viewer(xml,allModel=True):
    ''' Rupert's xslt view '''
    assert(allModel,True,'Support for not processing the entire model is not yet included')
    # we need the xml in a temporary file
    tmpfname=os.mktemp('.xml')
    tmpf=open(tmpfname,'w')
    tmpf.write(xml)
    # prettify the xml file with an xsl stylesheet
    outf=os.mktemp('.tmp')
    formatter=os.path.join(XSLDIR,'xmlformat.xsl')
    os.system('xsltproc %s %s > %s'%(formatter,tmpf,outf))
    os.system("mv %s %s"%(outf,tmpf))

    # create and return html rendered xml using an xsl stylesheet
    formatter=os.path.join(XSLDIR,'xmlverbatim.xsl')
    os.system('xsltproc %s %s > %s'%(formatter,tmpf,outf))

    # read html file
    file=open(outf, 'r')
    linestring=file.read()
    file.close()
    os.remove(outf)

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
      
       