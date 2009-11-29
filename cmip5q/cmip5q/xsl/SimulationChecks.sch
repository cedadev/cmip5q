<schema xmlns="http://www.ascc.net/xml/schematron" xmlns:xsl="tmp.none">
     <pattern name="[TBA] Check for conformance against numerical requirement constraints">
          <!-- This rule can not be checked by a schema checker as the CIM knows nothing about the numerical requirement constraints -->
          <rule context="/IGNORE">
               <!-- TBA -->
               <assert test="TBA">TBA</assert>
          </rule>
     </pattern>
     <pattern name="Check that all Inputs have been satisfied">
          <!-- Can this rule be checked by a schema checker ??? -->
          <rule context="/CIMRecord//Q_NumericalModel//modelComponent/composition/coupling">
               <!-- Q_closure is not output by q2cim unless a closure has been created -->
               <assert test=".//Q_closure">Model input &quot;<value-of select="Q_inputAbbrev"/>&quot; of type &quot;<value-of select="Q_inputType"/>&quot; from component &quot;<value-of select="Q_sourceComponent"/>&quot; has no closure</assert>
          </rule>
     </pattern>
     <pattern name="Check that all Numerical Requirements have been satisfied">
          <!-- Can this rule be checked by a schema checker ??? -->
          <rule context="/CIMRecord//Q_NumericalRequirements/Q_NumericalRequirement">
               <!-- Q_Value is not output by q2cim unless one or more conformances has been created -->
               <assert test="Q_Conformances//Q_Value">Numerical Requirement &quot;<value-of select="Q_Name"/>&quot; has no associated conformance</assert>
          </rule>
     </pattern>
</schema>
