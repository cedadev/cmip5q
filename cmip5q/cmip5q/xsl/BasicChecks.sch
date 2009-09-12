<schema xmlns="http://www.ascc.net/xml/schematron" xmlns:xsl="tmp.none">
     <pattern name="Check that every attribute has a value">
          <!-- This rule (for the questionnaire data) can not be checked by a schema checker as the CIM allows properties to have no value -->
          <rule context="/CIMRecord//modelComponent/componentProperties/componentProperty">
               <assert test="string-length(value)>0">Attribute &quot;<value-of select="shortName"/>&quot; in component &quot;<value-of select="ancestor::modelComponent/shortName"/>&quot; has no value.</assert>
          </rule>
     </pattern>
</schema>
