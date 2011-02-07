<!-- vi:set filetype=xml: -->
<schema xmlns="http://www.ascc.net/xml/schematron" >
 <ns prefix="cim" uri="http://www.metaforclimate.eu/schema/cim/1.5" />
 <ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd" />
 <ns prefix="gco" uri="http://www.isotc211.org/2005/gco" />
  <pattern name="Completeness requirements">
    <rule context="//componentProperty[count(componentProperty)=0]" >
      <assert test="string-length(shortName) > 0">
        Each leaf <name /> must possess a non-empty shortName element.
      </assert>
       <assert test="string-length(value) > 0">
        Each leaf <name /> <value-of select="../shortName" />::<value-of select="shortName" /> must possess a non-empty value element.
      </assert> 
   </rule>
   <rule context="//documentAuthor[@citationContact]" >
      <assert test="contains(gmd:CI_ResponsibleParty/gmd:electronicMailAddress/gco:CharacterString, '@')">
        Each citation contact author must have an email address specified.
      </assert>
    </rule>
    <rule context="//simulationRun/responsibleParty[gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode[@codeListValue != 'centre']]" >
      <assert test="contains(gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString, '@')">
        Simulation contact <value-of select="gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString" /> <value-of select="gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString" /> must have an email address specified.
      </assert>
    </rule>
  </pattern>
  <pattern name="Simulation Conformances fulfilment requirements">
    <rule context="numericalRequirement/*/name">
      <assert test="//simulationRun/conformance/requirement/reference[name = current()]">
        Simulation Conformance <value-of select="current()" /> must be fully specified.
      </assert>
    </rule>
  </pattern>
  <pattern name="Simulation Conformances consistency and completeness requirements">
    <rule context="//simulationRun/conformance[comment()='Conformance type : Via Inputs']">
      <assert test="string-length(source)>0">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Input conformance but does not declare any Input.
      </assert>
      <assert test="not(source/reference/change/detail[@type='CodeChange'])">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Input conformance but has specified a Model Mod.
      </assert>
    </rule>
    <rule context="//simulationRun/conformance[comment()='Conformance type : Via Model Mods']" >
      <assert test="string-length(source)>0">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Model Mod conformance but does not specify any Model Mod.
      </assert>
      <assert test="not(source/reference/type='componentProperty')"> 
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Model Mod conformance but has specified an Input <value-of select="source/reference/name"/>.
      </assert>
    </rule>
  </pattern>
  <pattern name="Model initial condition inputs requirements">
<!--    <rule context="childComponent/modelComponent/componentProperties/componentProperty[@represented][count(componentProperty)=0][(count(units)=1) or (count(cfName)=1)]"> -->
    <rule context="childComponent/modelComponent/componentProperties/componentProperty[@represented][count(componentProperty)=0][shortName=(//conformance/source/reference/name)]" >
<!--      <assert test="childComponent/modelComponent/componentProperties/componentProperty[@represented][count(cim        :componentProperty)=0][shortName=current() " >
      </assert> 
    </rule> -->
      <assert test="string-length(longName)>0">
        Model Component attribute <value-of select="shortName" /> in Component <value-of select="../../shortName"/> has no longName field.
      </assert>
      <assert test="string-length(description)>0">
        Model Component attribute <value-of select="shortName" /> in Component <value-of select="../../shortName"/> has no description field.
      </assert>
      <assert test="string-length(units/@value)>0">
        Model Component attribute <value-of select="shortName" /> in Component <value-of select="../../shortName"/> has no units specified.
      </assert>
    </rule>
  </pattern>
<!--  <pattern name="Either Units or CF type must be specified for initial condition inputs">
    <rule context="//childComponent/modelComponent/componentProperties/componentProperty[@represented][count(componentProperty)=0]">
      <assert test="not( (string-length(units/@value)>0) and (string-length(cfName)>0) )">
        Either a CF Type *or* a Units Type must be specified for <value-of select="shortName"/> initial condition inputs in Component <value-of select="../../shortName"/>.
      </assert>
    </rule>
  </pattern> -->
  <pattern name="Document Genealogy coherence check">
    <rule context="//documentGenealogy/relationship/documentRelationship/description">
      <assert test="string-length(//documentGenealogy/relationship/documentRelationship/target/reference/name)>0">
        Document Genealogy <value-of select="current()" /> in <value-of select="../../../../shortName"/> refers to an unspecified previous version.
      </assert>
    </rule>
  </pattern>
  <pattern name="Compiler specification coherence check">
    <rule context="//platform/compiler">
      <assert test="not( (string-length(compilerVersion)>0) and (string-length(compilerName)=0) )">
        A compiler version cannot be specified without a compiler name in platform <value-of select="../machine/machineName"/>.
      </assert>
    </rule>
  </pattern>
  <pattern name="Component Property value NA must exclude all others">
   <rule context="//componentProperty[count(value)>1]">
      <assert test="not( value='N/A' and (count(value)>1) )">
        Component Property <value-of select="shortName"/> in Component <value-of select="../../../shortName"/> set to NA yet includes other values.
      </assert>
    </rule>
  </pattern>
  <pattern name="Ensemble Constraints" >
     <rule context="//ensembleMember" >
      <assert test="string-length(description) > 0" >
       A description must be provided for each Ensemble member in Simulation <value-of select="current()/simulation/reference/name"/>.
      </assert>
      <assert test="count(..//ensembleMember/simulation/reference[change[1][name = current()/simulation/reference/change[1]/name]][change[last()][name = current()/simulation/reference/change[last()]/name]]/name)&lt;2" >
<!--        Ensemble member uniqueness constraint: <value-of select="simulation/reference/change[1]/name" />  and <value-of select="simulation/reference/change[last()]/name" /> from <value-of select="count(..//ensembleMember/simulation/reference[change[1][name = current()/simulation/reference/change[1]/name]][change[last()][name = current()/simulation/reference/change[last()]/name]]/name)" /> -->
        An Ensemble member's mods must be unique within an Ensemble: Mod combination <value-of select="simulation/reference/change[1]/name" /> and <value-of select="simulation/reference/change[last()]/name" /> occurs multiple times within Ensemble for Simulation <value-of select="current()/simulation/reference/name" />
      </assert>
    </rule>
  </pattern>
  <pattern name="Specific Component Property Constraints">
    <rule context="//componentProperty[shortName='AerosolTimeStepFramework']/componentProperty[shortName='Method'][contains(value,'operator splitting')]">
      <assert test="(string-length(../componentProperty[shortName='AdvectionTimeStep']/value)>0) and (string-length(../componentProperty[shortName='PhysicalTimeStep']/value)>0)">
      In Aerosol Key Properties, where Method is Specific time stepping (operator splitting), values must be provided for AdvectionTimeStep and PhysicalTimeStep.
      </assert> 
   </rule>
     <rule context="//componentProperty[shortName='AerosolTimeStepFramework']/componentProperty[shortName='Method'][contains(value,'integrated')]">
      <assert test="(string-length(../componentProperty[shortName='TimeStep']/value)>0) and (string-length(../componentProperty[shortName='SchemeType']/value)>0)">
      In Aerosol Key Properties, where Method is Specific time stepping (integrated), values must be provided for TimeStep and SchemeType.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'climatology')]">
      <assert test="(string-length(../componentProperty[shortName='ClimatologyType']/value)>0) and (string-length(../componentProperty[shortName='SpeciesEmitted']/value)>0)">
        In Aerosol Emission And Conc, where 2D-Emissions Method is prescribed (climatology), values must be provided for ClimatologyType and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'spatially')]">
      <assert test="string-length(../componentProperty[shortName='EmittedSpecies']/value)>0">
        In Aerosol Emission And Conc, where 2D-Emissions Method is prescribed (spatially uniform), a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'interactive')]">
      <assert test="string-length(../componentProperty[shortName='EmittedSpecies']/value)>0">
        In Aerosol Emission And Conc, where 2D-Emissions Method is interactive, a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'other')]">
      <assert test="(string-length(../componentProperty[shortName='MethodCharacteristics']/value)>0) and (string-length(../componentProperty[shortName='EmittedSpecies']/value)>0)">
        In Aerosol Emission And Conc, where 2D-Emissions Method is other, values must be provided for MethodCharacteristics and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='3D-Emissions']" >
      <assert test="(string-length(componentProperty[shortName='Method']/value>0) ) and (string-length(componentProperty[shortName='SourceTypes']/value)>0) ">
        In Aerosol Emission And Conc, values must be provided for both 3D-Emissions Method and SourceTypes.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'climatology')]">
      <assert test="(string-length(../componentProperty[shortName='ClimatologyType']/value)>0) and (string-length(../componentProperty[shortName='EmittedSpecies']/value)>0)">
        In Aerosol Emission And Conc, where 3D-Emissions Method is prescribed (climatology), values must be provided for ClimatologyType and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'spatially')]">
      <assert test="string-length(../componentProperty[shortName='EmittedSpecies']/value)>0">
        In Aerosol Emission And Conc, where 3D-Emissions Method is prescribed (spatially uniform), a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'interactive')]">
      <assert test="string-length(../componentProperty[shortName='EmittedSpecies']/value)>0">
        In Aerosol Emission And Conc, where 3D-Emissions Method is interactive, a value must be provided for SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Emission And Conc']/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method'][contains(value[last()],'other')]">
      <assert test="(string-length(../componentProperty[shortName='MethodCharacteristics']/value)>0) and (string-length(../componentProperty[shortName='EmittedSpecies']/value)>0)">
        In Aerosol Emission And Conc, where 3D-Emissions Method is other, values must be provided for MethodCharacteristics and SpeciesEmitted.
      </assert> 
    </rule>
    <rule context="//modelComponent[shortName='Atmos Convect Turbul Cloud']/componentProperties/componentProperty[shortName='BoundaryLayerTurbulence']/componentProperty[shortName='SchemeName'][contains(value[last()],'Mellor-Yamada')]">
      <assert test="string-length(../componentProperty[shortName='ClosureOrder']/value)>0">
        In AtmosConvectTurbulCloud, where the BoundaryLayerTurbulence SchemeName is Mellor-Yamada, a value must be specified for the ClosureOrder field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Atmos Convect Turbul Cloud']/componentProperties/componentProperty[shortName='DeepConvection']/componentProperty[shortName='SchemeType'][contains(value[last()],'Mass-flux')]">
      <assert test="string-length(../componentProperty[shortName='SchemeMethod']/value)>0">
        In AtmosConvectTurbulCloud, where the DeepConvection SchemeType is Mass-Flux, a value must be specified for the SchemeMethod field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Atmos Convect Turbul Cloud']/componentProperties/componentProperty[shortName='ShallowConvection']/componentProperty[shortName='Method'][contains(value[last()],'separated')]">
      <assert test="(string-length(../componentProperty[shortName='SchemeName']/value)>0) and (string-length(../componentProperty[shortName='SchemeType']/value)>0)">
        In AtmosConvectTurbulCloud, where the ShallowConvection Method is separated, values must be specified for both the SchemeName and SchemeType fields.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Atmos Dynamical Core']/componentProperties/componentProperty[shortName='HorizontalDiscretization']/componentProperty[shortName='SchemeType'][contains(value[last()],'fixed grid')]">
      <assert test="string-length(../componentProperty[shortName='SchemeMethod']/value)>0">
        In AtmosDynamicalCore, where the HorizontalDiscretization SchemeType is fixed grid, a value must be specified for the SchemeMethod field.
      </assert>
      <assert test="not ( (contains(../componentProperty[shortName='SchemeMethod']/value,'finite differences')) and (string-length(../componentProperty[shortName='SchemeOrder']/value)=0) ) ">
        In AtmosDynamicalCore, where SchemeType is Fixed Grid and SchemeMethod is either Finite Differences or Centered Finite Differences, a value must be specified for the SchemeOrder field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Atmos Key Properties']/componentProperties/componentProperty[shortName='VolcanoesImplementation'][contains(value[last()],'via stratospheric aerosols optical thickness')]">
      <assert test="string-length(../componentProperty[shortName='VolcanoesImplementationMethod']/value)>0">
        In AtmosKeyProperties, where the VolcanoesImplementation is via stratospheric aerosols optical thickness, a value must be specified for the VolcanoesImplementationMethod field.
      </assert>
    </rule>
    <rule context="//componentProperty[shortName='Orography']/componentProperty[shortName='OrographyType'][value='modified']" >
      <assert test="string-length(../componentProperty[shortName='OrographyChanges']/value)>0" >
        In AtmosKeyProperties, where the OrographyType includes the type modified, a value must be specified for the OrographyChanges field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Transport']/componentProperties/componentProperty[shortName='Method'][contains(value, 'specific transport scheme')]" >
      <assert test="(string-length(../componentProperty[shortName='SchemeType']/value)>0) and (string-length(../componentProperty[shortName='MassConservation']/value)>0) and (string-length(../componentProperty[shortName='Convection']/value)>0) " >
        In AerosolTransport, where the Method is specified to be a Specific Transport Scheme, values must be provided for each of the SchemeType, MassConservation and Convection fields.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Aerosol Transport']/componentProperties/componentProperty[shortName='Turbulence']/componentProperty[shortName='Method'][contains(value, 'specific turbulence scheme')]" >
      <assert test="string-length(../componentProperty[shortName='Scheme']/value)>0" >
        In AerosolTransport, where the Turbulence Method is Specific Turbulence Scheme, a value must be specified in the Scheme field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Sea Ice Key Properties']/componentProperties/componentProperty[shortName='SeaIceRepresentation']/componentProperty[shortName='SchemeType'][contains(value,'multi-levels')]" >
      <assert test="string-length(../componentProperty[shortName='Multi-LevelsScheme']/value)>0" >
        In Sea Ice Key Properties, where the SeaIceRepresentation SchemeType is Multi-Levels, a value must be specified in the Multi-LevelsScheme field.
      </assert>
    </rule>
    <rule context="//modelComponent[shortName='Sea Ice Key Properties']/componentProperties/componentProperty[shortName='TimeSteppingFramework']/componentProperty[shortName='Method'][contains(value,'specific time step')]" >
      <assert test="string-length(../componentProperty[shortName='TimeStep']/value)>0" >
        In Sea Ice Key Properties, where the TimeSteppingFramework methods include Specific Time Step, a value must be specified for the TimeStep field.
      </assert>
    </rule>
  </pattern>
  <pattern name="Model component AerosolKeyProperties constraints">
    <rule context="//modelComponent[type[@value='AerosolKeyProperties']]/componentProperties/componentProperty[shortName='AerosolTimeStepFramework']/componentProperty[shortName='Method']">
      <assert test="not ( (value='specific time stepping (operator splitting)') and (string-length(../componentProperty[shortName='AdvectionTimeStep']/value)=0) )">Model component AerosolKeyProperties, Parameter AerosolTimeStepFramework: Where Method is specific time stepping (operator splitting), a value must be specified for AdvectionTimeStep</assert>
      <assert test="not ( (value='specific time stepping (operator splitting)') and (string-length(../componentProperty[shortName='PhysicalTimeStep']/value)=0) )">Model component AerosolKeyProperties, Parameter AerosolTimeStepFramework: Where Method is specific time stepping (operator splitting), a value must be specified for PhysicalTimeStep</assert>
      <assert test="not ( (value='specific time stepping (integrated)') and (string-length(../componentProperty[shortName='TimeStep']/value)=0) )">Model component AerosolKeyProperties, Parameter AerosolTimeStepFramework: Where Method is specific time stepping (integrated), a value must be specified for TimeStep</assert>
      <assert test="not ( (value='specific time stepping (integrated)') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component AerosolKeyProperties, Parameter AerosolTimeStepFramework: Where Method is specific time stepping (integrated), a value must be specified for SchemeType</assert>
    </rule>
  </pattern>
  <pattern name="Model component AerosolTransport constraints">
    <rule context="//modelComponent[type[@value='AerosolTransport']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='Method']">
      <assert test="not ( (value='specific transport scheme') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component AerosolTransport, Parameter General Attributes: Where Method is specific transport scheme, a value must be specified for SchemeType</assert>
      <assert test="not ( (value='specific transport scheme') and (string-length(../componentProperty[shortName='MassConservation']/value)=0) )">Model component AerosolTransport, Parameter General Attributes: Where Method is specific transport scheme, a value must be specified for MassConservation</assert>
      <assert test="not ( (value='specific transport scheme') and (string-length(../componentProperty[shortName='Convection']/value)=0) )">Model component AerosolTransport, Parameter General Attributes: Where Method is specific transport scheme, a value must be specified for Convection</assert>
    </rule>
    <rule context="//modelComponent[type[@value='AerosolTransport']]/componentProperties/componentProperty[shortName='Turbulence']/componentProperty[shortName='Method']">
      <assert test="not ( (value='specific turbulence scheme') and (string-length(../componentProperty[shortName='Scheme']/value)=0) )">Model component AerosolTransport, Parameter Turbulence: Where Method is specific turbulence scheme, a value must be specified for Scheme</assert>
    </rule>
  </pattern>
  <pattern name="Model component AerosolEmissionAndConc constraints">
    <rule context="//modelComponent[type[@value='AerosolEmissionAndConc']]/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method']">
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='prescribed (climatology)ClimatologyType']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='prescribed (climatology)SpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='prescribed (spatially uniform)SpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='interactiveSpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has interactive, a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherMethodCharacteristics']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherSpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for SpeciesEmitted</assert>
    </rule>
    <rule context="//modelComponent[type[@value='AerosolEmissionAndConc']]/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method']">
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='prescribed (climatology)ClimatologyType']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='prescribed (climatology)SpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='prescribed (spatially uniform)SpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='interactiveSpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has interactive, a value must be specified for SpeciesEmitted</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherMethodCharacteristics']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherSpeciesEmitted']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for SpeciesEmitted</assert>
    </rule>
  </pattern>
  <pattern name="Model component AerosolModel constraints">
    <rule context="//modelComponent[type[@value='AerosolModel']]/componentProperties/componentProperty[shortName='AerosolScheme']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='bulk') and (string-length(../componentProperty[shortName='bulkSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bulk, a value must be specified for Species</assert>
      <assert test="not ( (value='modal') and (string-length(../componentProperty[shortName='modalFramework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has modal, a value must be specified for Framework</assert>
      <assert test="not ( (value='modal') and (string-length(../componentProperty[shortName='modalSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has modal, a value must be specified for Species</assert>
      <assert test="not ( (value='bin') and (string-length(../componentProperty[shortName='binFramework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bin, a value must be specified for Framework</assert>
      <assert test="not ( (value='bin') and (string-length(../componentProperty[shortName='binSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bin, a value must be specified for Species</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherSchemeType']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for SchemeType</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherFramework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for Framework</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='otherSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for Species</assert>
    </rule>
  </pattern>

</schema>
