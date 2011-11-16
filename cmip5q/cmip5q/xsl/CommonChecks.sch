<!-- vi:set filetype=xml: -->
<schema xmlns="http://www.ascc.net/xml/schematron" >
 <ns prefix="cim" uri="http://www.metaforclimate.eu/schema/cim/1.5" />
 <ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd" />
 <ns prefix="gco" uri="http://www.isotc211.org/2005/gco" />
  <pattern name="Completeness requirements">
    <rule context="//componentProperty[count(componentProperty)=0][string-length(units/@value)=0][value]" >
      <assert test="string-length(shortName) > 0">
        Each leaf <name /> must possess a non-empty shortName element.
      </assert>
<!--       <assert test="(string-length(shortName) > 0) or (string-length(value) > 0)"> -->
       <assert test="string-length(value) > 0">
        Each leaf <name /> <value-of select="../../../shortName" />::<value-of select="../../shortName" />::<value-of select="../shortName" />::<value-of select="shortName" /> must possess a non-empty value element. 
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
<!-- 
  <pattern name="Simulation Conformances fulfilment requirements">
    <rule context="numericalRequirement/*/name">
      <assert test="//simulationRun/conformance/requirement/reference[name = current()]">
        Simulation Conformance <value-of select="current()" /> must be fully specified.
      </assert>
    </rule>
  </pattern>
-->
  <pattern name="Simulation Conformances consistency and completeness requirements">
    <rule context="//simulationRun/conformance[comment()='type : via inputs']">
<!--      <assert test="string-length(source)>0">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Input conformance but does not declare any Input.
      </assert> -->
      <assert test="not(source/reference/change/detail[@type='CodeChange'])">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Input conformance but has specified a Model Mod.
      </assert>
    </rule>
    <rule context="//simulationRun/conformance[comment()='type : via model mods']" >
      <assert test="string-length(source)>0">
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Model Mod conformance but does not specify any Model Mod.
      </assert>
<!--      <assert test="not(source/reference/type='componentProperty')"> 
        Simulation Conformance <value-of select="requirement/reference/name"/> claims Model Mod conformance but has specified an Input <value-of select="source/reference/name"/>.
      </assert> -->
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
  <pattern name="Either Units or CF type must be specified for initial condition inputs">
    <rule context="//childComponent/modelComponent/componentProperties/componentProperty[@represented][count(componentProperty)=0]">
      <assert test="not( (string-length(units[@value])>0) and (string-length(cfName)>0) )">
        Either a CF Type *or* a Units Type must be specified for <value-of select="shortName"/> initial condition inputs in Component <value-of select="../../shortName"/>.
      </assert>
    </rule>
  </pattern>
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
<!--   <rule context="//componentProperty[count(value)>1]"> -->
   <rule context="//componentProperty">
      <assert test="not( value='N/A' and (count(value)>1) )">
        Component Property <value-of select="shortName"/> in Component <value-of select="../../../shortName"/> set to NA yet includes other values.
      </assert>
    </rule>
  </pattern>
  <pattern name="Ensemble Constraints" >
     <rule context="//ensembleMember" >
      <assert test="string-length(simulation/reference/description) > 0" >
       A description must be provided for each Ensemble member in Simulation <value-of select="current()/simulation/reference/name"/>.
      </assert>
    </rule>
  </pattern>

  <pattern name="Simulation authorsList">
    <rule context="//simulationRun/authorsList">
      <assert test="string-length(list)!=0">
        Values must be provided for the list element of a Simulation authorsList.
      </assert>
    </rule>
  </pattern>

<!-- GRID RULES BEGIN -->

<pattern name="General Grid Rules">
  <rule context="//gridSpec/esmModelGrid">
    <assert test="string-length(shortName)!=0">
      Grid: A value must be provided for Grid Short Name.
    </assert>
    <assert test="string-length(longName)!=0">
      Grid <value-of select="shortName" />: A value must be provided for Grid Long Name.
    </assert>
    <assert test="string-length(description)!=0">
      Grid <value-of select="shortName" />: A value must be provided for Grid Description.
    </assert>
    <assert test="string-length(gridTile/@discretizationType)!=0">
      Grid <value-of select="shortName" />: A value must be provided for GridDiscretization.
    </assert>
  </rule>
</pattern>


  <pattern name="Grid Specification constraints">
    <rule context="//gridSpec/esmModelGrid/gridTile" >

      <assert test="string-length(horizontalResolution/@description) != 0">
          In Grid <value-of select="../shortName" />, section horizontalResolution, values must be provided for both GridResolution and GridRefinementScheme.
         <value-of select="horizontalResolution/@description" />
      </assert>

      <assert test="(string-length(extent/latMin)!=0) and (string-length(extent/latMax)!=0) and (string-length(extent/lonMin)!=0) and (string-length(extent/lonMax)!=0)" >
        In Grid <value-of select="../shortName" />, section horizontalResolution::HorizontalExtent, values must be provided for each of LatMin, LatMax, LonMin and LonMax
      </assert>

      <assert test="not((@discretizationType='logically_rectangular') and not((../../esmModelGrid[@gridType = 'regular_gaussian']) or (../../esmModelGrid[@gridType = 'other']) or (../../esmModelGrid[@gridType = 'displaced_pole']) or (../../esmModelGrid[@gridType = 'tripolar']) or (../../esmModelGrid[@gridType = 'cubed_sphere']) or (../../esmModelGrid[@gridType = 'regular_lat_lon']))) ">
          Grid Specification: Where GridDiscretization is 'logically_rectangular', GridType must be one of 'regular_gaussian', 'displaced_pole', 'tripolar', 'cubed_sphere', 'latitude-longitude' or 'other'
      </assert>

      <assert test="not( ( (@discretizationType='logically_rectangular') and (../../esmModelGrid[@gridType = 'regular_lat_lon']) ) and ( (string-length(horizontalResolution/property[name='NumberOfLatitudinalGridCells']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfLongitudinalGridCells']/value)=0) )  )">
        Grid Specification: Where GridDiscretization is 'logically_rectangular' and GridType is 'latitude-longitude', values must be provided for both 'NumberOfLatitudinalGridCells' and 'NumberOfLongitudinalGridCells'
      </assert>

      <assert test="not( ( (@discretizationType='unstructured_polygonal') and (../../esmModelGrid[@gridType = 'reduced_gaussian']) ) and ( (string-length(horizontalResolution/property[name='NumberOfTotalGridPoints']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfLatitudePointsPoleToEquator']/value)=0) )  )">
        Grid Specification: Where GridDiscretization is 'unstructured_polygonal' and GridType is 'reduced_gaussian', values must be provided for both 'NumberOfTotalGridPoints' and 'NumberOfLatitudePointsPoleToEquator'
      </assert>

      <assert test="not( ( (@discretizationType='logically_rectangular') and (../../esmModelGrid[@gridType = 'regular_gaussian']) ) and ( (string-length(horizontalResolution/property[name='NumberOfLongitudinalGridPoints']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfLatitudePointsPoleToEquator']/value)=0) )  )">
        Grid Specification: Where GridDiscretization is 'logically_rectangular' and GridType is 'regular_gaussian', values must be provided for both 'NumberOfLongitudinalGridPoints' and 'NumberOfLatitudePointsPoleToEquator'
      </assert>

      <assert test="not( ( (@discretizationType='logically_rectangular') and (../../esmModelGrid[@gridType = 'displaced_pole']) ) and ( (string-length(horizontalResolution/property[name='NumberOfCellsInSecondGridDimension']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfCellsInFirstGridDimension']/value)=0) or (string-length(horizontalResolution/property[name='FirstPoleLat']/value)=0) or (string-length(horizontalResolution/property[name='SecondPoleLat']/value)=0) or (string-length(horizontalResolution/property[name='FirstPoleLon']/value)=0) or (string-length(horizontalResolution/property[name='SecondPoleLon']/value)=0)  )  )">
        Grid Specification: Where GridDiscretization is 'logically_rectangular' and GridType is 'displaced pole', values must be provided for 'NumberOfCellsInFirstGridDimension', 'NumberOfCellsInSecondGridDimension', 'FirstPoleLat', 'FirstPoleLon', 'SecondPoleLat' and 'SecondPoleLon'
      </assert>

      <assert test="not( ( (@discretizationType='logically_rectangular') and (../../esmModelGrid[@gridType = 'cubed_sphere']) ) and ( (string-length(horizontalResolution/property[name='NumberOfCellsInFirstGridDimension']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfCellsInSecondGridDimension']/value)=0) )  )">
        Grid Specification: Where GridDiscretization is 'logically_rectangular' and GridType is 'cubed sphere', values must be provided for both 'NumberOfCellsInFirstGridDimension' and 'NumberOfCellsInSecondGridDimension'
      </assert>

      <assert test="not( ( (@discretizationType='structured_triangular') and (../../esmModelGrid[@gridType = 'icosahedral']) ) and ( (string-length(horizontalResolution/property[name='NumberOfGridsCellsInFirstDimensionOfDiamond']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfGridsCellsInSecondDimensionOfDiamond']/value)=0) )  )">
        Grid Specification: Where GridDiscretization is 'structured_triangular' and GridType is 'icosahedral', values must be provided for both 'NumberOfGridsCellsInFirstDimensionOfDiamond' and 'NumberOfGridsCellsInSecondDimensionOfDiamond'
      </assert>

      <assert test="not( ( (@discretizationType='logically_rectangular') and (../../esmModelGrid[@gridType = 'tripolar']) ) and ( (string-length(horizontalResolution/property[name='NumberOfCellsInFirstGridDimension']/value)=0) or (string-length(horizontalResolution/property[name='NumberOfCellsInSecondGridDimension']/value)=0) or (string-length(horizontalResolution/property[name='FirstPoleLat']/value)=0) or (string-length(horizontalResolution/property[name='FirstPoleLon']/value)=0) or (string-length(horizontalResolution/property[name='SecondPoleLat']/value)=0) or (string-length(horizontalResolution/property[name='SecondPoleLon']/value)=0) or (string-length(horizontalResolution/property[name='ThirdPoleLat']/value)=0) or (string-length(horizontalResolution/property[name='ThirdPoleLon']/value)=0)  )  )">
        Grid Specification: Where GridDiscretization is 'logically_rectangular' and GridType is 'tripolar', values must be provided for 'NumberOfCellsInFirstGridDimension' and 'NumberOfCellsInSecondGridDimension', and for each of 'FirstPoleLat, 'FirstPoleLon', 'SecondPoleLat', 'SecondPoleLon', 'ThirdPoleLat' and 'ThirdPoleLon'
      </assert>

      <assert test="not((@discretizationType='unstructured_polygonal') and not((../../esmModelGrid[@gridType = 'reduced_gaussian']) or (../../esmModelGrid[@gridType = 'other']))) " >
        Grid Specification: Where GridDiscretization is 'unstructured polygonal', either 'reduced gaussian' or 'other' must be specified for GridType
      </assert>

      <assert test="not((@discretizationType='structured_triangular') and not((../../esmModelGrid[@gridType = 'icosahedral']) or (../../esmModelGrid[@gridType = 'other']))) " >
        Grid Specification: Where GridDiscretization is 'structured triangular', either 'icosahedral' or 'other' must be specified for GridType
      </assert>

      <assert test="not((@discretizationType='spherical_harmonics') and (string-length(horizontalResolution/property[name='SpectralTruncatureNumber']/value)=0) ) " >
        Grid Specification: Where GridDiscretization is 'spherical_harmonics', a value must be provided for 'SpectralTruncatureNumber'
      </assert>

<!-- Vertical Rules Begin -->

      <assert test="not( string-length(zcoords/@coordinateType)=0)">
        In Grid <value-of select="../shortName" />, a value must be provided for 'VerticalCoordinateType'.
      </assert>

      <assert test="not( (zcoords/@coordinateType='terrain-following') and not( (zcoords/@coordinateForm='sigma') or (zcoords/@coordinateForm='S-coordinate') or (zcoords/@coordinateForm='other')) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'terrain-following', 'VerticalCoordinate' must be one of 'sigma', 'S-Coordinate' or 'other'.
      </assert>    

      <assert test="not( (zcoords/@coordinateType='terrain-following') and (string-length(zcoords/property[name='SurfaceReference']/value)=0) )">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'terrain-following', a value must be provided for 'SurfaceReference'
      </assert>

      <assert test="not( (zcoords/@coordinateType='space-based') and not( (zcoords/@coordinateForm='geometric height') or (zcoords/@coordinateForm='depth') or (zcoords/@coordinateForm='sleve (smooth level)') or (zcoords/@coordinateForm='other')) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'space-based', 'VerticalCoordinate' must be one of 'geometric height', 'depth', 'sleve (smooth level)' or 'other'
      </assert>    

      <assert test="not( (zcoords/@coordinateType='mass-based') and not( (zcoords/@coordinateForm='Z*-coordinate') or (zcoords/@coordinateForm='isopycnic') or (zcoords/@coordinateForm='isentropic') or (zcoords/@coordinateForm='pressure') or (zcoords/@coordinateForm='natural log pressure') or (zcoords/@coordinateForm='pressure-height') or (zcoords/@coordinateForm='P*-coordinate') or (zcoords/@coordinateForm='Z-coordinate') or (zcoords/@coordinateForm='Z**-coordinate') or (zcoords/@coordinateForm='other') ) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'mass-based', 'VerticalCoordinate' must be one of 'isopycnic', 'isentropic', 'pressure', 'natural log pressure', 'pressure-height', 'Z*-coordinate', 'P*-coordinate', 'Z-coordinate', 'Z**-coordinate' or 'other'
      </assert>    

      <assert test="not( (zcoords/@coordinateType='mass-based') and (string-length(zcoords/property[name='SurfaceReference']/value)=0) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'mass-based', a value must be provided for 'SurfaceReference'
      </assert>    

      <assert test="not( ( (zcoords/@coordinateForm='Z*-coordinate') or (zcoords/@coordinateForm='Z-coordinate') ) and (string-length(zcoords/property[name='PartialSteps']/value)=0) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinate' is either 'Z*-coordinate' or 'Z-coordinate', a value must be provided for 'PartialSteps'
      </assert>

      <assert test="not( (zcoords/@coordinateType='hybrid') and not( (zcoords/@coordinateForm='hybrid floating Lagrangian') or (zcoords/@coordinateForm='hybrid sigma-pressure') or (zcoords/@coordinateForm='hybrid height') or (zcoords/@coordinateForm='hybrid sigma-z') or (zcoords/@coordinateForm='double sigma') or (zcoords/@coordinateForm='hybrid Z-S') or (zcoords/@coordinateForm='hybrid Z-isopycnic') or (zcoords/@coordinateForm='other') ) ) ">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'hybrid', 'VerticalCoordinate' must be one of 'hybrid floating Lagrangian', 'hybrid sigma-pressure', 'hybrid height', 'hybrid sigma-z', 'double sigma', 'hybrid Z-S', 'hybrid Z-isopycnic' or 'other' 
      </assert>    

      <assert test="not( (zcoords/@coordinateType='hybrid') and (string-length(zcoords/property[name='Hybridization']/value)=0) )">
        In Grid <value-of select="../shortName" />, section Vertical Coordinate System, where 'VerticalCoordinateType' is 'hybrid', a value must be provided for 'Hybridization'
      </assert>

      <assert test="not( (comment()='Vertical Domain specified as : atmospheric') and ( (string-length(verticalResolution/property[name='TopModelLevel']/value)=0) or (string-length(verticalResolution/property[name='NumberOfLevelsBelow850hPa']/value)=0) or (string-length(verticalResolution/property[name='NumberOfLevelsAbove200hPa']/value)=0) or (string-length(verticalResolution/property[name='NumberOfLevels']/value)=0)) )">
        In Grid <value-of select="../shortName" />, section 'Vertical Extent', where <value-of select="comment()" />, values must be provided for each of 'NumberOfLevels', 'TopModelLevel', 'NumberOfLevelsBelow850hPa' and 'NumberOfLevelsAbove200hPa'
      </assert>

<assert test="not( (comment()='Vertical Domain specified as : oceanic') and ( (string-length(verticalResolution/property[name='NumberOfLevels']/value)=0) or (string-length(verticalResolution/property[name='LowerLevel']/value)=0) or (string-length(verticalResolution/property[name='UpperLevel']/value)=0) or (string-length(verticalResolution/property[name='NumberOfLevelsInUpper100m']/value)=0)) )">
        In Grid <value-of select="../shortName" />, section 'Vertical Extent', where <value-of select="comment()" />, values must be provided for each of 'NumberOfLevels', 'LowerLevel', 'UpperLevel' and 'NumberOfLevelsInUpper100m'
      </assert>
<!-- Vertical Rules End -->

<!-- HERE -->
    </rule>
    <rule context="//gridSpec/esmModelGrid/gridMosaic" >

      <assert test="not((@gridtype='composite') and not((string-length(../../esmModelGrid/@gridType) = 0) )  ) " >
        Grid Specification: Where GridDiscretization is 'composite', at least one value must be provided for 'CompositeGridDiscretization'
      </assert>

      <assert test="not((@gridType='composite') and not((../../esmModelGrid[@gridType = 'icosahedral']) or (../../esmModelGrid[@gridType = 'other']))) " >
        Grid Specification: 'CompositeGridDiscretization'
      </assert>


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
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimatologyType']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimEmittedSpecies</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='UniformEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for UniformEmittedSpecies</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='InteractivEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has interactive, a value must be specified for InteractivEmittedSpecies</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='MethodCharacteristics']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='EmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for EmittedSpecies</assert>
    </rule>
    <rule context="//modelComponent[type[@value='AerosolEmissionAndConc']]/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method']">
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimatologyType']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimEmittedSpecies</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='UniformEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for UniformEmittedSpecies</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='InteractivEmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has interactive, a value must be specified for InteractivEmittedSpecies</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='MethodCharacteristics']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='EmittedSpecies']/value)=0) )">Model component AerosolEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for EmittedSpecies</assert>
    </rule>
  </pattern>
  <pattern name="Model component AerosolModel constraints">
    <rule context="//modelComponent[type[@value='AerosolModel']]/componentProperties/componentProperty[shortName='AerosolScheme']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='bulk') and (string-length(../componentProperty[shortName='BulkSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bulk, a value must be specified for BulkSpecies</assert>
      <assert test="not ( (value='modal') and (string-length(../componentProperty[shortName='ModalFramework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has modal, a value must be specified for ModalFramework</assert>
      <assert test="not ( (value='modal') and (string-length(../componentProperty[shortName='ModalSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has modal, a value must be specified for ModalSpecies</assert>
      <assert test="not ( (value='bin') and (string-length(../componentProperty[shortName='BinFramework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bin, a value must be specified for BinFramework</assert>
      <assert test="not ( (value='bin') and (string-length(../componentProperty[shortName='BinSpecies']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has bin, a value must be specified for BinSpecies</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='SchemeCharacteritics']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for SchemeCharacteritics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='Framework']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for Framework</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='Species']/value)=0) )">Model component AerosolModel, Parameter AerosolScheme: Where SchemeType has other, a value must be specified for Species</assert>
    </rule>
  </pattern>
  <pattern name="Model component AtmosAdvection constraints">
    <rule context="//modelComponent[type[@value='AtmosAdvection']]/componentProperties/componentProperty[shortName='Momentum']/componentProperty[shortName='SchemeCharacteristics']">
      <assert test="not ( (value='staggered grid') and (string-length(../componentProperty[shortName='StaggeringType']/value)=0) )">Model component AtmosAdvection, Parameter Momentum: Where SchemeCharacteristics has staggered grid, a value must be specified for StaggeringType</assert>
    </rule>
  </pattern>
  <pattern name="Model component AtmosRadiation constraints"/>
  <pattern name="Model component AtmosCloudScheme constraints"/>
  <pattern name="Model component CloudSimulator constraints"/>
  <pattern name="Model component AtmosOrographyAndWaves constraints"/>
  <pattern name="Model component AtmChemTransport constraints"/>
  <pattern name="Model component AtmChemEmissionAndConc constraints">
    <rule context="//modelComponent[type[@value='AtmChemEmissionAndConc']]/componentProperties/componentProperty[shortName='2D-Emissions']/componentProperty[shortName='Method']">
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimatologyType']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimEmittedSpecies</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='UniformEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for UniformEmittedSpecies</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='InteractivEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has interactive, a value must be specified for InteractivEmittedSpecies</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='MethodCharacteristics']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='EmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 2D-Emissions: Where Method has other, a value must be specified for EmittedSpecies</assert>
    </rule>
    <rule context="//modelComponent[type[@value='AtmChemEmissionAndConc']]/componentProperties/componentProperty[shortName='3D-Emissions']/componentProperty[shortName='Method']">
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimatologyType']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimatologyType</assert>
      <assert test="not ( (value='prescribed (climatology)') and (string-length(../componentProperty[shortName='ClimEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (climatology), a value must be specified for ClimEmittedSpecies</assert>
      <assert test="not ( (value='prescribed (spatially uniform)') and (string-length(../componentProperty[shortName='UniformEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has prescribed (spatially uniform), a value must be specified for UniformEmittedSpecies</assert>
      <assert test="not ( (value='interactive') and (string-length(../componentProperty[shortName='InteractivEmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has interactive, a value must be specified for InteractivEmittedSpecies</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='MethodCharacteristics']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for MethodCharacteristics</assert>
      <assert test="not ( (value='other') and (string-length(../componentProperty[shortName='EmittedSpecies']/value)=0) )">Model component AtmChemEmissionAndConc, Parameter 3D-Emissions: Where Method has other, a value must be specified for EmittedSpecies</assert>
    </rule>
  </pattern>
  <pattern name="Model component AtmChemGasPhaseChemistry constraints"/>
  <pattern name="Model component StratosphericHeterChem constraints"/>
  <pattern name="Model component TroposphericHeterChem constraints"/>
  <pattern name="Model component AtmChemPhotoChemistry constraints">
    <rule context="//modelComponent[type[@value='AtmChemPhotoChemistry']]/componentProperties/componentProperty[shortName='Photolysis']/componentProperty[shortName='Method']">
      <assert test="not ( (value='online') and (string-length(../componentProperty[shortName='Processes']/value)=0) )">Model component AtmChemPhotoChemistry, Parameter Photolysis: Where Method is online, a value must be specified for Processes</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandIceGlaciers constraints">
    <rule context="//modelComponent[type[@value='LandIceGlaciers']]/componentProperties/componentProperty[shortName='SnowTreatment']/componentProperty[shortName='Method']">
      <assert test="not ( (value='different from Snow in LandSurface') and (string-length(../componentProperty[shortName='NumberOfSnowLayers']/value)=0) )">Model component LandIceGlaciers, Parameter SnowTreatment: Where Method is different from Snow in LandSurface, a value must be specified for NumberOfSnowLayers</assert>
      <assert test="not ( (value='different from Snow in LandSurface') and (string-length(../componentProperty[shortName='Properties']/value)=0) )">Model component LandIceGlaciers, Parameter SnowTreatment: Where Method is different from Snow in LandSurface, a value must be specified for Properties</assert>
    </rule>
  </pattern>
  <pattern name="Model component IceSheetDynamics constraints">
    <rule context="//modelComponent[type[@value='IceSheetDynamics']]/componentProperties/componentProperty[shortName='Model-Numerics']/componentProperty[shortName='TimeSteppingMethod']">
      <assert test="not ( (value='specific time step') and (string-length(../componentProperty[shortName='TimeStep']/value)=0) )">Model component IceSheetDynamics, Parameter Model-Numerics: Where TimeSteppingMethod is specific time step, a value must be specified for TimeStep</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandIceShelvesDynamics constraints">
    <rule context="//modelComponent[type[@value='LandIceShelvesDynamics']]/componentProperties/componentProperty[shortName='Model-Numerics']/componentProperty[shortName='TimeSteppingMethod']">
      <assert test="not ( (value='specific time step') and (string-length(../componentProperty[shortName='TimeStep']/value)=0) )">Model component LandIceShelvesDynamics, Parameter Model-Numerics: Where TimeSteppingMethod is specific time step, a value must be specified for TimeStep</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandSurfSoilHydrology constraints">
    <rule context="//modelComponent[type[@value='LandSurfSoilHydrology']]/componentProperties/componentProperty[shortName='Runoff-Drainage']/componentProperty[shortName='Method']">
      <assert test="not ( (value='differentiated drainage and runoff') and (string-length(../componentProperty[shortName='Processes']/value)=0) )">Model component LandSurfSoilHydrology, Parameter Runoff-Drainage: Where Method is differentiated drainage and runoff, a value must be specified for Processes</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandSurfSoilHeatTreatment constraints"/>
  <pattern name="Model component LandSurfaceSnow constraints"/>
  <pattern name="Model component LandSurfaceVegetation constraints">
    <rule context="//modelComponent[type[@value='LandSurfaceVegetation']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='VegetationRepresentation']">
      <assert test="not ( (value='biome types') and (string-length(../componentProperty[shortName='BiomeTypes']/value)=0) )">Model component LandSurfaceVegetation, Parameter General Attributes: Where VegetationRepresentation is biome types, a value must be specified for BiomeTypes</assert>
      <assert test="not ( (value='vegetation types') and (string-length(../componentProperty[shortName='VegetationTypes']/value)=0) )">Model component LandSurfaceVegetation, Parameter General Attributes: Where VegetationRepresentation is vegetation types, a value must be specified for VegetationTypes</assert>
    </rule>
    <rule context="//modelComponent[type[@value='LandSurfaceVegetation']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='VegetationTimeVariation']">
      <assert test="not ( (value='fixed&quot; or &quot;prescribed') and (string-length(../componentProperty[shortName='VegetationMap']/value)=0) )">Model component LandSurfaceVegetation, Parameter General Attributes: Where VegetationTimeVariation is fixed" or "prescribed, a value must be specified for VegetationMap</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandSurfaceEnergyBalance constraints">
    <rule context="//modelComponent[type[@value='LandSurfaceEnergyBalance']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='SpecificTiling']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SubsurfaceTiling']/value)=0) )">Model component LandSurfaceEnergyBalance, Parameter General Attributes: Where SpecificTiling is yes, a value must be specified for SubsurfaceTiling</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandSurfaceAlbedo constraints">
    <rule context="//modelComponent[type[@value='LandSurfaceAlbedo']]/componentProperties/componentProperty[shortName='SnowFreeAlbedo']/componentProperty[shortName='Type']">
      <assert test="not ( (value='prognostic') and (string-length(../componentProperty[shortName='FunctionOf']/value)=0) )">Model component LandSurfaceAlbedo, Parameter SnowFreeAlbedo: Where Type is prognostic, a value must be specified for FunctionOf</assert>
      <assert test="not ( (value='prognostic') and (string-length(../componentProperty[shortName='Direct-Diffuse']/value)=0) )">Model component LandSurfaceAlbedo, Parameter SnowFreeAlbedo: Where Type is prognostic, a value must be specified for Direct-Diffuse</assert>
      <assert test="not ( (value='prognostic') and (string-length(../componentProperty[shortName='NumberOfWavelenghBands']/value)=0) )">Model component LandSurfaceAlbedo, Parameter SnowFreeAlbedo: Where Type is prognostic, a value must be specified for NumberOfWavelenghBands</assert>
    </rule>
    <rule context="//modelComponent[type[@value='LandSurfaceAlbedo']]/componentProperties/componentProperty[shortName='SnowAlbedo']/componentProperty[shortName='Type']">
      <assert test="not ( (value='prognostic') and (string-length(../componentProperty[shortName='FunctionOf']/value)=0) )">Model component LandSurfaceAlbedo, Parameter SnowAlbedo: Where Type is prognostic, a value must be specified for FunctionOf</assert>
    </rule>
  </pattern>
  <pattern name="Model component VegetationCarbonCycle constraints">
    <rule context="//modelComponent[type[@value='VegetationCarbonCycle']]/componentProperties/componentProperty[shortName='AutotrophicRespiration']/componentProperty[shortName='Method']">
      <assert test="not ( (value='parametrized') and (string-length(../componentProperty[shortName='MaintenanceRespiration']/value)=0) )">Model component VegetationCarbonCycle, Parameter AutotrophicRespiration: Where Method is parametrized, a value must be specified for MaintenanceRespiration</assert>
    </rule>
  </pattern>
  <pattern name="Model component RiverRouting constraints">
    <rule context="//modelComponent[type[@value='RiverRouting']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='CouplingWithAtmosphere']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='QuantitiesExchangedWithAtmosphere']/value)=0) )">Model component RiverRouting, Parameter General Attributes: Where CouplingWithAtmosphere is yes, a value must be specified for QuantitiesExchangedWithAtmosphere</assert>
    </rule>
  </pattern>
  <pattern name="Model component LandSurfaceLakes constraints">
    <rule context="//modelComponent[type[@value='LandSurfaceLakes']]/componentProperties/componentProperty[shortName='General Attributes']/componentProperty[shortName='CouplingWithRivers']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='QuantitiesExchangedWithRivers']/value)=0) )">Model component LandSurfaceLakes, Parameter General Attributes: Where CouplingWithRivers is yes, a value must be specified for QuantitiesExchangedWithRivers</assert>
    </rule>
  </pattern>
  <pattern name="Model component ModelComponentGrid constraints">
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='HorizontalProperties']/componentProperty[shortName='GridDiscretization']">
      <assert test="not ( (value='spherical harmonics') and (string-length(../componentProperty[shortName='SpectralTruncatureNumber']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is spherical harmonics, a value must be specified for SpectralTruncatureNumber</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='CompositeGridDiscretization']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is composite, a value must be specified for CompositeGridDiscretization</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is composite, a value must be specified for GridType</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='CompositeGrid']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is composite, a value must be specified for CompositeGrid</assert>
      <assert test="not ( (value='logically rectangular') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is logically rectangular, a value must be specified for GridType</assert>
      <assert test="not ( (value='structured triangular') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is structured triangular, a value must be specified for GridType</assert>
      <assert test="not ( (value='unstructured polygonal') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridDiscretization is unstructured polygonal, a value must be specified for GridType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='HorizontalProperties']/componentProperty[shortName='GridType']">
      <assert test="not ( (value='latitude-longitude') and (string-length(../componentProperty[shortName='NumberOfLongitudinalGridCells']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is latitude-longitude, a value must be specified for NumberOfLongitudinalGridCells</assert>
      <assert test="not ( (value='latitude-longitude') and (string-length(../componentProperty[shortName='NumberOfLatitudinalGridCells']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is latitude-longitude, a value must be specified for NumberOfLatitudinalGridCells</assert>
      <assert test="not ( (value='regular gaussian') and (string-length(../componentProperty[shortName='NumberOfLongitudinalGridPoints']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is regular gaussian, a value must be specified for NumberOfLongitudinalGridPoints</assert>
      <assert test="not ( (value='regular gaussian') and (string-length(../componentProperty[shortName='NumberOfLatitudePointsPoleToEquator']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is regular gaussian, a value must be specified for NumberOfLatitudePointsPoleToEquator</assert>
      <assert test="not ( (value='reduced gaussian') and (string-length(../componentProperty[shortName='NumberOfTotalGridPoints']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is reduced gaussian, a value must be specified for NumberOfTotalGridPoints</assert>
      <assert test="not ( (value='reduced gaussian') and (string-length(../componentProperty[shortName='NumberOfLatitudePointsPoleToEquator']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is reduced gaussian, a value must be specified for NumberOfLatitudePointsPoleToEquator</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='FirstPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for FirstPoleLat</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='FirstPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for FirstPoleLon</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='SecondPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for SecondPoleLat</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='SecondPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for SecondPoleLon</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is displaced pole, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='cubed sphere') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is cubed sphere, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='cubed sphere') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is cubed sphere, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='icosahedral geodesic') and (string-length(../componentProperty[shortName='NumberOfGridsCellsInFirstDimensionOfDiamond']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is icosahedral geodesic, a value must be specified for NumberOfGridsCellsInFirstDimensionOfDiamond</assert>
      <assert test="not ( (value='icosahedral geodesic') and (string-length(../componentProperty[shortName='NumberOfGridsCellsInSecondDimensionOfDiamond']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is icosahedral geodesic, a value must be specified for NumberOfGridsCellsInSecondDimensionOfDiamond</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='FirstPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for FirstPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='FirstPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for FirstPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='SecondPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for SecondPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='SecondPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for SecondPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='ThirdPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for ThirdPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='ThirdPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for ThirdPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is tripolar, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='ying yang') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstTileDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is ying yang, a value must be specified for NumberOfCellsInFirstTileDimension</assert>
      <assert test="not ( (value='ying yang') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondTileDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalProperties: Where GridType is ying yang, a value must be specified for NumberOfCellsInSecondTileDimension</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='HorizontalCoordinateSystem']/componentProperty[shortName='GridDiscretization']">
      <assert test="not ( (value='spherical harmonics') and (string-length(../componentProperty[shortName='SpectralTruncatureNumber']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is spherical harmonics, a value must be specified for SpectralTruncatureNumber</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='CompositeGridDiscretization']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is composite, a value must be specified for CompositeGridDiscretization</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is composite, a value must be specified for GridType</assert>
      <assert test="not ( (value='composite') and (string-length(../componentProperty[shortName='CompositeGrid']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is composite, a value must be specified for CompositeGrid</assert>
      <assert test="not ( (value='logically rectangular') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is logically rectangular, a value must be specified for GridType</assert>
      <assert test="not ( (value='structured triangular') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is structured triangular, a value must be specified for GridType</assert>
      <assert test="not ( (value='unstructured polygonal') and (string-length(../componentProperty[shortName='GridType']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridDiscretization is unstructured polygonal, a value must be specified for GridType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='HorizontalCoordinateSystem']/componentProperty[shortName='GridType']">
      <assert test="not ( (value='latitude-longitude') and (string-length(../componentProperty[shortName='NumberOfLongitudinalGridCells']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is latitude-longitude, a value must be specified for NumberOfLongitudinalGridCells</assert>
      <assert test="not ( (value='latitude-longitude') and (string-length(../componentProperty[shortName='NumberOfLatitudinalGridCells']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is latitude-longitude, a value must be specified for NumberOfLatitudinalGridCells</assert>
      <assert test="not ( (value='regular gaussian') and (string-length(../componentProperty[shortName='NumberOfLongitudinalGridPoints']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is regular gaussian, a value must be specified for NumberOfLongitudinalGridPoints</assert>
      <assert test="not ( (value='regular gaussian') and (string-length(../componentProperty[shortName='NumberOfLatitudePointsPoleToEquator']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is regular gaussian, a value must be specified for NumberOfLatitudePointsPoleToEquator</assert>
      <assert test="not ( (value='reduced gaussian') and (string-length(../componentProperty[shortName='NumberOfTotalGridPoints']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is reduced gaussian, a value must be specified for NumberOfTotalGridPoints</assert>
      <assert test="not ( (value='reduced gaussian') and (string-length(../componentProperty[shortName='NumberOfLatitudePointsPoleToEquator']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is reduced gaussian, a value must be specified for NumberOfLatitudePointsPoleToEquator</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='FirstPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for FirstPoleLat</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='FirstPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for FirstPoleLon</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='SecondPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for SecondPoleLat</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='SecondPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for SecondPoleLon</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='displaced pole') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is displaced pole, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='cubed sphere') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is cubed sphere, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='cubed sphere') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is cubed sphere, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='icosahedral geodesic') and (string-length(../componentProperty[shortName='NumberOfGridsCellsInFirstDimensionOfDiamond']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is icosahedral geodesic, a value must be specified for NumberOfGridsCellsInFirstDimensionOfDiamond</assert>
      <assert test="not ( (value='icosahedral geodesic') and (string-length(../componentProperty[shortName='NumberOfGridsCellsInSecondDimensionOfDiamond']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is icosahedral geodesic, a value must be specified for NumberOfGridsCellsInSecondDimensionOfDiamond</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='FirstPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for FirstPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='FirstPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for FirstPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='SecondPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for SecondPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='SecondPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for SecondPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='ThirdPoleLat']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for ThirdPoleLat</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='ThirdPoleLon']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for ThirdPoleLon</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for NumberOfCellsInFirstGridDimension</assert>
      <assert test="not ( (value='tripolar') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondGridDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is tripolar, a value must be specified for NumberOfCellsInSecondGridDimension</assert>
      <assert test="not ( (value='ying yang') and (string-length(../componentProperty[shortName='NumberOfCellsInFirstTileDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is ying yang, a value must be specified for NumberOfCellsInFirstTileDimension</assert>
      <assert test="not ( (value='ying yang') and (string-length(../componentProperty[shortName='NumberOfCellsInSecondTileDimension']/value)=0) )">Model component ModelComponentGrid, Parameter HorizontalCoordinateSystem: Where GridType is ying yang, a value must be specified for NumberOfCellsInSecondTileDimension</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalProperties']/componentProperty[shortName='VerticalCoordinateType']">
      <assert test="not ( (value='terrain-following') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is terrain-following, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='terrain-following') and (string-length(../componentProperty[shortName='SurfaceReference']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is terrain-following, a value must be specified for SurfaceReference</assert>
      <assert test="not ( (value='space-based') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is space-based, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='mass-based') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is mass-based, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='mass-based') and (string-length(../componentProperty[shortName='SurfaceReference']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is mass-based, a value must be specified for SurfaceReference</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalProperties']/componentProperty[shortName='VerticalCoordinate']">
      <assert test="not ( (value='Z-coordinate&quot; or &quot;Z*-coordinate') and (string-length(../componentProperty[shortName='PartialSteps']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinate is Z-coordinate" or "Z*-coordinate, a value must be specified for PartialSteps</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalProperties']/componentProperty[shortName='VerticalCoordinateType']">
      <assert test="not ( (value='hybrid') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is hybrid, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='hybrid') and (string-length(../componentProperty[shortName='Hybridization']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where VerticalCoordinateType is hybrid, a value must be specified for Hybridization</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalProperties']/componentProperty[shortName='Domain']">
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevels']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is atmospheric, a value must be specified for NumberOfLevels</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='TopModelLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is atmospheric, a value must be specified for TopModelLevel</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevelsBelow850hPa']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is atmospheric, a value must be specified for NumberOfLevelsBelow850hPa</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevelsAbove200hPa']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is atmospheric, a value must be specified for NumberOfLevelsAbove200hPa</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='NumberOfLevels']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is oceanic, a value must be specified for NumberOfLevels</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='NumberOfLevelsInUpper100m']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is oceanic, a value must be specified for NumberOfLevelsInUpper100m</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='UpperLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is oceanic, a value must be specified for UpperLevel</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='LowerLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalProperties: Where Domain is oceanic, a value must be specified for LowerLevel</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalCoordinateSystem']/componentProperty[shortName='VerticalCoordinateType']">
      <assert test="not ( (value='terrain-following') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is terrain-following, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='terrain-following') and (string-length(../componentProperty[shortName='SurfaceReference']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is terrain-following, a value must be specified for SurfaceReference</assert>
      <assert test="not ( (value='space-based') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is space-based, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='mass-based') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is mass-based, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='mass-based') and (string-length(../componentProperty[shortName='SurfaceReference']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is mass-based, a value must be specified for SurfaceReference</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalCoordinateSystem']/componentProperty[shortName='VerticalCoordinate']">
      <assert test="not ( (value='Z-coordinate&quot; or &quot;Z*-coordinate') and (string-length(../componentProperty[shortName='PartialSteps']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinate is Z-coordinate" or "Z*-coordinate, a value must be specified for PartialSteps</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalCoordinateSystem']/componentProperty[shortName='VerticalCoordinateType']">
      <assert test="not ( (value='hybrid') and (string-length(../componentProperty[shortName='VerticalCoordinate']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is hybrid, a value must be specified for VerticalCoordinate</assert>
      <assert test="not ( (value='hybrid') and (string-length(../componentProperty[shortName='Hybridization']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalCoordinateSystem: Where VerticalCoordinateType is hybrid, a value must be specified for Hybridization</assert>
    </rule>
    <rule context="//modelComponent[type[@value='ModelComponentGrid']]/componentProperties/componentProperty[shortName='VerticalExtent']/componentProperty[shortName='Domain']">
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevels']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is atmospheric, a value must be specified for NumberOfLevels</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='TopModelLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is atmospheric, a value must be specified for TopModelLevel</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevelsBelow850hPa']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is atmospheric, a value must be specified for NumberOfLevelsBelow850hPa</assert>
      <assert test="not ( (value='atmospheric') and (string-length(../componentProperty[shortName='NumberOfLevelsAbove200hPa']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is atmospheric, a value must be specified for NumberOfLevelsAbove200hPa</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='NumberOfLevels']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is oceanic, a value must be specified for NumberOfLevels</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='NumberOfLevelsInUpper100m']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is oceanic, a value must be specified for NumberOfLevelsInUpper100m</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='UpperLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is oceanic, a value must be specified for UpperLevel</assert>
      <assert test="not ( (value='oceanic') and (string-length(../componentProperty[shortName='LowerLevel']/value)=0) )">Model component ModelComponentGrid, Parameter VerticalExtent: Where Domain is oceanic, a value must be specified for LowerLevel</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanBioBoundaryForcing constraints"/>
  <pattern name="Model component OceanBioGasExchange constraints">
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='CO2']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter CO2: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='O2']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter O2: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='DMS']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter DMS: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='N2']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter N2: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='N2O']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter N2O: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioGasExchange']]/componentProperties/componentProperty[shortName='CO']/componentProperty[shortName='Present']">
      <assert test="not ( (value='yes') and (string-length(../componentProperty[shortName='SchemeType']/value)=0) )">Model component OceanBioGasExchange, Parameter CO: Where Present is yes, a value must be specified for SchemeType</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanBioTracersEcosystem constraints">
    <rule context="//modelComponent[type[@value='OceanBioTracersEcosystem']]/componentProperties/componentProperty[shortName='Phytoplancton']/componentProperty[shortName='Type']">
      <assert test="not ( (value='list') and (string-length(../componentProperty[shortName='ListOfSpecies']/value)=0) )">Model component OceanBioTracersEcosystem, Parameter Phytoplancton: Where Type is list, a value must be specified for ListOfSpecies</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanBioTracersEcosystem']]/componentProperties/componentProperty[shortName='Zooplancton']/componentProperty[shortName='Type']">
      <assert test="not ( (value='list') and (string-length(../componentProperty[shortName='ListOfSpecies']/value)=0) )">Model component OceanBioTracersEcosystem, Parameter Zooplancton: Where Type is list, a value must be specified for ListOfSpecies</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanBioChemistry constraints"/>
  <pattern name="Model component OceanAdvection constraints"/>
  <pattern name="Model component OceanLateralPhysMomentum constraints">
    <rule context="//modelComponent[type[@value='OceanLateralPhysMomentum']]/componentProperties/componentProperty[shortName='EddyViscosityCoefficient']/componentProperty[shortName='CoefficientType']">
      <assert test="not ( (value='constant') and (string-length(../componentProperty[shortName='CoefficientValue']/value)=0) )">Model component OceanLateralPhysMomentum, Parameter EddyViscosityCoefficient: Where CoefficientType is constant, a value must be specified for CoefficientValue</assert>
      <assert test="not ( (value='space varying&quot; or &quot;time + space varying') and (string-length(../componentProperty[shortName='SpatialVariation']/value)=0) )">Model component OceanLateralPhysMomentum, Parameter EddyViscosityCoefficient: Where CoefficientType is space varying" or "time + space varying, a value must be specified for SpatialVariation</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanLateralPhysTracers constraints">
    <rule context="//modelComponent[type[@value='OceanLateralPhysTracers']]/componentProperties/componentProperty[shortName='EddyViscosityCoefficient']/componentProperty[shortName='CoefficientType']">
      <assert test="not ( (value='constant') and (string-length(../componentProperty[shortName='CoefficientValue']/value)=0) )">Model component OceanLateralPhysTracers, Parameter EddyViscosityCoefficient: Where CoefficientType is constant, a value must be specified for CoefficientValue</assert>
      <assert test="not ( (value='space varying') and (string-length(../componentProperty[shortName='SpatialVariation']/value)=0) )">Model component OceanLateralPhysTracers, Parameter EddyViscosityCoefficient: Where CoefficientType is space varying, a value must be specified for SpatialVariation</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanLateralPhysTracers']]/componentProperties/componentProperty[shortName='Eddy-inducedVelocity']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='GM scheme') and (string-length(../componentProperty[shortName='CoefficientType']/value)=0) )">Model component OceanLateralPhysTracers, Parameter Eddy-inducedVelocity: Where SchemeType is GM scheme, a value must be specified for CoefficientType</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanLateralPhysTracers']]/componentProperties/componentProperty[shortName='Eddy-inducedVelocity']/componentProperty[shortName='CoefficientType']">
      <assert test="not ( (value='constant') and (string-length(../componentProperty[shortName='CoefficientValue']/value)=0) )">Model component OceanLateralPhysTracers, Parameter Eddy-inducedVelocity: Where CoefficientType is constant, a value must be specified for CoefficientValue</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanMixedLayer constraints">
    <rule context="//modelComponent[type[@value='OceanMixedLayer']]/componentProperties/componentProperty[shortName='Tracers']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='turbulent closure') and (string-length(../componentProperty[shortName='ClosureOrder']/value)=0) )">Model component OceanMixedLayer, Parameter Tracers: Where SchemeType is turbulent closure, a value must be specified for ClosureOrder</assert>
      <assert test="not ( (value='constant values') and (string-length(../componentProperty[shortName='MixingCoefficient']/value)=0) )">Model component OceanMixedLayer, Parameter Tracers: Where SchemeType is constant values, a value must be specified for MixingCoefficient</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanMixedLayer']]/componentProperties/componentProperty[shortName='Momentum']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='turbulent closure') and (string-length(../componentProperty[shortName='ClosureOrder']/value)=0) )">Model component OceanMixedLayer, Parameter Momentum: Where SchemeType is turbulent closure, a value must be specified for ClosureOrder</assert>
      <assert test="not ( (value='constant values') and (string-length(../componentProperty[shortName='MixingCoefficient']/value)=0) )">Model component OceanMixedLayer, Parameter Momentum: Where SchemeType is constant values, a value must be specified for MixingCoefficient</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanInteriorMixing constraints">
    <rule context="//modelComponent[type[@value='OceanInteriorMixing']]/componentProperties/componentProperty[shortName='Tracers']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='constant values') and (string-length(../componentProperty[shortName='MixingCoefficient']/value)=0) )">Model component OceanInteriorMixing, Parameter Tracers: Where SchemeType is constant values, a value must be specified for MixingCoefficient</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanInteriorMixing']]/componentProperties/componentProperty[shortName='Tracers']/componentProperty[shortName='BackgroundType']">
      <assert test="not ( (value='constant value') and (string-length(../componentProperty[shortName='BackgroundCoefficient']/value)=0) )">Model component OceanInteriorMixing, Parameter Tracers: Where BackgroundType is constant value, a value must be specified for BackgroundCoefficient</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanInteriorMixing']]/componentProperties/componentProperty[shortName='Momentum']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='constant values') and (string-length(../componentProperty[shortName='MixingCoefficient']/value)=0) )">Model component OceanInteriorMixing, Parameter Momentum: Where SchemeType is constant values, a value must be specified for MixingCoefficient</assert>
    </rule>
    <rule context="//modelComponent[type[@value='OceanInteriorMixing']]/componentProperties/componentProperty[shortName='Momentum']/componentProperty[shortName='BackgroundType']">
      <assert test="not ( (value='constant value') and (string-length(../componentProperty[shortName='BackgroundCoefficient']/value)=0) )">Model component OceanInteriorMixing, Parameter Momentum: Where BackgroundType is constant value, a value must be specified for BackgroundCoefficient</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanUpAndLowBoundaries constraints">
    <rule context="//modelComponent[type[@value='OceanUpAndLowBoundaries']]/componentProperties/componentProperty[shortName='BottomBoundaryLayer']/componentProperty[shortName='Type']">
      <assert test="not ( (value='diffusive') and (string-length(../componentProperty[shortName='LateralMixingCoefficient']/value)=0) )">Model component OceanUpAndLowBoundaries, Parameter BottomBoundaryLayer: Where Type is diffusive, a value must be specified for LateralMixingCoefficient</assert>
    </rule>
  </pattern>
  <pattern name="Model component OceanBoundForcingTracers constraints">
    <rule context="//modelComponent[type[@value='OceanBoundForcingTracers']]/componentProperties/componentProperty[shortName='SunlightPenetration']/componentProperty[shortName='SchemeType']">
      <assert test="not ( (value='extinction depth') and (string-length(../componentProperty[shortName='FirstDepth']/value)=0) )">Model component OceanBoundForcingTracers, Parameter SunlightPenetration: Where SchemeType is extinction depth, a value must be specified for FirstDepth</assert>
      <assert test="not ( (value='extinction depth') and (string-length(../componentProperty[shortName='SecondDepth']/value)=0) )">Model component OceanBoundForcingTracers, Parameter SunlightPenetration: Where SchemeType is extinction depth, a value must be specified for SecondDepth</assert>
      <assert test="not ( (value='extinction depth') and (string-length(../componentProperty[shortName='ThirdDepth']/value)=0) )">Model component OceanBoundForcingTracers, Parameter SunlightPenetration: Where SchemeType is extinction depth, a value must be specified for ThirdDepth</assert>
    </rule>
  </pattern>
  <pattern name="Model component SeaIceThermodynamics constraints">
    <rule context="//modelComponent[type[@value='SeaIceThermodynamics']]/componentProperties/componentProperty[shortName='Ice']/componentProperty[shortName='VerticalHeatDiffusion']">
      <assert test="not ( (value='multi-layer') and (string-length(../componentProperty[shortName='NumberOfLayers']/value)=0) )">Model component SeaIceThermodynamics, Parameter Ice: Where VerticalHeatDiffusion is multi-layer, a value must be specified for NumberOfLayers</assert>
    </rule>
  </pattern>
  <pattern name="Model component SeaIceDynamics constraints"/>
</schema>
