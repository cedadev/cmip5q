<!-- vi:set number filetype=xml: -->
<schema xmlns="http://www.ascc.net/xml/schematron" >
 <ns prefix="cim" uri="http://www.metaforclimate.eu/schema/cim/1.5" />
 <ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd" />
 <ns prefix="gco" uri="http://www.isotc211.org/2005/gco" />
  <pattern name="Completeness requirements">
    <rule context="//cim:componentProperty[count(cim:componentProperty)=0]" >
      <assert test="string-length(cim:shortName) > 0">
        Each leaf <name /> must possess a non-empty shortName element.
      </assert>
    </rule>
    <rule context="//cim:documentAuthor[@citationContact]" >
      <assert test="contains(gmd:CI_ResponsibleParty/gmd:electronicMailAddress/gco:CharacterString, '@')">
        Each citation contact author must have an email address specified.
      </assert>
    </rule>
    <rule context="//cim:ensembleMember" >
      <assert test="string-length(cim:description) > 0" >
        Each ensemble member must have a description.
      </assert>
    </rule>
  </pattern>
  <pattern name="Simulation Conformances fulfilment requirements">
    <rule context="cim:numericalRequirement/cim:name">
      <assert test="//cim:simulationRun/cim:conformance/cim:requirement/cim:reference[cim:name = current()]">
        Simulation Conformance <value-of select="current()" /> must be fully specified.
      </assert>
    </rule>
  </pattern>
  <pattern name="Simulation Conformances consistency and completeness requirements">
    <rule context="//cim:simulationRun/cim:conformance[comment()='Conformance type : Via Inputs']">
      <assert test="string-length(cim:source)>0">
        Simulation Conformance <value-of select="cim:requirement/cim:reference/cim:name"/> claims Input conformance but does not declare any Input.
      </assert>
      <assert test="not(cim:source/cim:reference/cim:change/cim:detail[@type='CodeChange'])">
        Simulation Conformance <value-of select="cim:requirement/cim:reference/cim:name"/> claims Input conformance but has specified a Model Mod.
      </assert>
    </rule>
    <rule context="//cim:simulationRun/cim:conformance[comment()='Conformance type : Via Model Mods']" >
      <assert test="string-length(cim:source)>0">
        Simulation Conformance <value-of select="cim:requirement/cim:reference/cim:name"/> claims Model Mod conformance but does not specify any Model Mod.
      </assert>
      <assert test="not(cim:source/cim:reference/cim:type='componentProperty')"> 
        Simulation Conformance <value-of select="cim:requirement/cim:reference/cim:name"/> claims Model Mod conformance but has specified an Input <value-of select="cim:source/cim:reference/cim:name"/>.
      </assert>
    </rule>
  </pattern>
  <pattern name="Model initial condition inputs requirements">
    <rule context="cim:childComponent/cim:modelComponent/cim:componentProperties/cim:componentProperty[@represented][count(cim:componentProperty)=0]">
      <assert test="string-length(cim:longName)>0">
        Model initial condition input <value-of select="cim:shortName" /> in Component <value-of select="../../cim:shortName"/> has no longName field.
      </assert>
      <assert test="string-length(cim:description)>0">
        Model initial condition input <value-of select="cim:shortName" /> in Component <value-of select="../../cim:shortName"/> has no description field.
      </assert>
      <assert test="string-length(cim:units/@value)>0">
        Model initial condition input <value-of select="cim:shortName" /> in Component <value-of select="../../cim:shortName"/> has no units specified.
      </assert>
    </rule>
  </pattern>
  <pattern name="Either Units or CF type must be specified for initial condition inputs">
    <rule context="//cim:childComponent/cim:modelComponent/cim:componentProperties/cim:componentProperty[@represented][count(cim:componentProperty)=0]">
      <assert test="not( (string-length(cim:units/@value)>0) and (string-length(cim:cfName)>0) )">
        Either a CF Type *or* a Units Type must be specified for <value-of select="cim:shortName"/> initial condition inputs in Component <value-of select="../../cim:shortName"/>.
      </assert>
<!--      <assert test="not( (string-length(cim:units/@value)=0) and (string-length(cim:cfName)=0) )">
        Either one of CF Type or Units Type must be specified for <value-of select="cim:shortName"/> initial condition inputs.
      </assert> -->
    </rule>
  </pattern>
  <pattern name="Document Genealogy coherence check">
    <rule context="//cim:documentGenealogy/cim:relationship/cim:documentRelationship/cim:description">
      <assert test="string-length(//cim:documentGenealogy/cim:relationship/cim:documentRelationship/cim:target/reference/name)>0">
        Document Genealogy <value-of select="current()" /> in <value-of select="../../../../cim:shortName"/> refers to an unspecified previous version.
      </assert>
    </rule>
  </pattern>
  <pattern name="Compiler specification coherence check">
    <rule context="//cim:platform/cim:compiler">
      <assert test="not( (string-length(cim:compilerVersion)>0) and (string-length(cim:compilerName)=0) )">
        A compiler version cannot be specified without a compiler name in platform <value-of select="../cim:machine/cim:machineName"/>.
      </assert>
    </rule>
  </pattern>
  <pattern name="Component Property value NA must exclude all others">
    <rule context="//cim:componentProperty">
      <assert test="not( cim:value='N/A' and (count(cim:value)>1) )">
        Component Property <value-of select="cim:shortName"/> in Component <value-of select="../../../cim:shortName"/> set to NA yet includes other values.
      </assert>
    </rule>
  </pattern>
  <pattern name="Specific Component Property Constraints">
    <rule context="//cim:componentProperty[cim:shortName='AerosolTimeStepFramework']/cim:componentProperty[cim:shortName='Method'][contains(cim:value,'operator splitting')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='AdvectionTimeStep']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='PhysicalTimeStep']/cim:value)>0)">
      In Aerosol Key Properties, where Method is Specific time stepping (operator splitting), values must be provided for AdvectionTimeStep and PhysicalTimeStep.
      </assert> 
   </rule>
     <rule context="//cim:componentProperty[cim:shortName='AerosolTimeStepFramework']/cim:componentProperty[cim:shortName='Method'][contains(cim:value,'integrated')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='TimeStep']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SchemeType']/cim:value)>0)">
      In Aerosol Key Properties, where Method is Specific time stepping (integrated), values must be provided for TimeStep and SchemeType.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='2D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'climatology')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='ClimatologyType']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0)">
        In Aerosol Emission And Conc, where 2D-Emissions Method is prescribed (climatology), values must be provided for ClimatologyType and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='2D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'spatially')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0">
        In Aerosol Emission And Conc, where 2D-Emissions Method is prescribed (spatially uniform), a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='2D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'interactive')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0">
        In Aerosol Emission And Conc, where 2D-Emissions Method is interactive, a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='2D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'other')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='MethodCharacteristics']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0)">
        In Aerosol Emission And Conc, where 2D-Emissions Method is other, values must be provided for MethodCharacteristics and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='3D-Emissions']" >
      <assert test="(string-length(cim:componentProperty[cim:shortName='Method']/cim:value>0) ) and (string-length(cim:componentProperty[cim:shortName='SourceTypes']/cim:value)>0) ">
        In Aerosol Emission And Conc, values must be provided for both 3D-Emissions Method and SourceTypes.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='3D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'climatology')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='ClimatologyType']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0)">
        In Aerosol Emission And Conc, where 3D-Emissions Method is prescribed (climatology), values must be provided for ClimatologyType and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='3D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'spatially')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0">
        In Aerosol Emission And Conc, where 3D-Emissions Method is prescribed (spatially uniform), a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='3D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'interactive')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0">
        In Aerosol Emission And Conc, where 3D-Emissions Method is interactive, a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Emission And Conc']/cim:componentProperties/cim:componentProperty[cim:shortName='3D-Emissions']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'other')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='MethodCharacteristics']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SpeciesEmitted']/cim:value)>0)">
        In Aerosol Emission And Conc, where 3D-Emissions Method is other, values must be provided for MethodCharacteristics and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Atmos Convect Turbul Cloud']/cim:componentProperties/cim:componentProperty[cim:shortName='BoundaryLayerTurbulence']/cim:componentProperty[cim:shortName='SchemeName'][contains(cim:value[last()],'Mellor-Yamada')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='ClosureOrder']/cim:value)>0">
        In AtmosConvectTurbulCloud, where the BoundaryLayerTurbulence SchemeName is Mellor-Yamada, a value must be specified for the ClosureOrder field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Atmos Convect Turbul Cloud']/cim:componentProperties/cim:componentProperty[cim:shortName='DeepConvection']/cim:componentProperty[cim:shortName='SchemeType'][contains(cim:value[last()],'Mass-flux')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SchemeMethod']/cim:value)>0">
        In AtmosConvectTurbulCloud, where the DeepConvection SchemeType is Mass-Flux, a value must be specified for the SchemeMethod field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Atmos Convect Turbul Cloud']/cim:componentProperties/cim:componentProperty[cim:shortName='ShallowConvection']/cim:componentProperty[cim:shortName='Method'][contains(cim:value[last()],'separated')]">
      <assert test="(string-length(../cim:componentProperty[cim:shortName='SchemeName']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='SchemeType']/cim:value)>0)">
        In AtmosConvectTurbulCloud, where the ShallowConvection Method is separated, values must be specified for both the SchemeName and SchemeType fields.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Atmos Dynamical Core']/cim:componentProperties/cim:componentProperty[cim:shortName='HorizontalDiscretization']/cim:componentProperty[cim:shortName='SchemeType'][contains(cim:value[last()],'fixed grid')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='SchemeMethod']/cim:value)>0">
        In AtmosDynamicalCore, where the HorizontalDiscretization SchemeType is fixed grid, a value must be specified for the SchemeMethod field.
      </assert>
      <assert test="not ( (contains(../cim:componentProperty[cim:shortName='SchemeMethod']/cim:value,'finite differences')) and (string-length(../cim:componentProperty[cim:shortName='SchemeOrder']/cim:value)=0) ) ">
        In AtmosDynamicalCore, where SchemeType is Fixed Grid and SchemeMethod is either Finite Differences or Centered Finite Differences, a value must be specified for the SchemeOrder field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Atmos Key Properties']/cim:componentProperties/cim:componentProperty[cim:shortName='VolcanoesImplementation'][contains(cim:value[last()],'via stratospheric aerosols optical thickness')]">
      <assert test="string-length(../cim:componentProperty[cim:shortName='VolcanoesImplementationMethod']/cim:value)>0">
        In AtmosKeyProperties, where the VolcanoesImplementation is via stratospheric aerosols optical thickness, a value must be specified for the VolcanoesImplementationMethod field.
      </assert>
    </rule>
    <rule context="//cim:componentProperty[cim:shortName='Orography']/cim:componentProperty[cim:shortName='OrographyType'][cim:value='modified']" >
      <assert test="string-length(../cim:componentProperty[cim:shortName='OrographyChanges']/cim:value)>0" >
        In AtmosKeyProperties, where the OrographyType includes the type modified, a value must be specified for the OrographyChanges field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Transport']/cim:componentProperties/cim:componentProperty[cim:shortName='Method'][contains(cim:value, 'specific transport scheme')]" >
      <assert test="(string-length(../cim:componentProperty[cim:shortName='SchemeType']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='MassConservation']/cim:value)>0) and (string-length(../cim:componentProperty[cim:shortName='Convection']/cim:value)>0) " >
        In AerosolTransport, where the Method is specified to be a Specific Transport Scheme, values must be provided for each of the SchemeType, MassConservation and Convection fields.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Aerosol Transport']/cim:componentProperties/cim:componentProperty[cim:shortName='Turbulence']/cim:componentProperty[cim:shortName='Method'][contains(cim:value, 'specific turbulence scheme')]" >
      <assert test="string-length(../cim:componentProperty[cim:shortName='Scheme']/cim:value)>0" >
        In AerosolTransport, where the Turbulence Method is Specific Turbulence Scheme, a value must be specified in the Scheme field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Sea Ice Key Properties']/cim:componentProperties/cim:componentProperty[cim:shortName='SeaIceRepresentation']/cim:componentProperty[cim:shortName='SchemeType'][contains(cim:value,'multi-levels')]" >
      <assert test="string-length(../cim:componentProperty[cim:shortName='Multi-LevelsScheme']/cim:value)>0" >
        In Sea Ice Key Properties, where the SeaIceRepresentation SchemeType is Multi-Levels, a value must be specified in the Multi-LevelsScheme field.
      </assert>
    </rule>
    <rule context="//cim:modelComponent[cim:shortName='Sea Ice Key Properties']/cim:componentProperties/cim:componentProperty[cim:shortName='TimeSteppingFramework']/cim:componentProperty[cim:shortName='Method'][contains(cim:value,'specific time step')]" >
      <assert test="string-length(../cim:componentProperty[cim:shortName='TimeStep']/cim:value)>0" >
        In Sea Ice Key Properties, where the TimeSteppingFramework methods include Specific Time Step, a value must be specified for the TimeStep field.
      </assert>
    </rule>

  </pattern>

</schema>
