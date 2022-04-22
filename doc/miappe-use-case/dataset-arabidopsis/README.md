# Source

Optimizing experimental procedures for quantitative evaluation of crop plant performance in high throughput phenotyping systems
[DOI](https://doi.org/10.3389/fpls.2014.00770)

[ISA-Tab files](http://dx.doi.org/10.5447/IPK/2014/4)

The experiment contains several measurement types, each having specific result types and data files.

Here, we consider the factor in the ISA-Tab, soil cover and plant movement.


# Modelling choices (TODO: PROVISIONAL, TO BE REVIEWED)

Most of the MIAPPE mapping work has been done within the ELIXIR plant community. Hereby, we 
describe some of the choices made.

## MIAPPE:Investigation
* Let's introduce agri:FieldTrialInvestigation as a subclass of schema:Dataset
* This is to reconcile the hackathon discussions (where it was clarified that Investigation is 
  intended as dataset) with the MIAPPE publication 
	(https://nph.onlinelibrary.wiley.com/doi/10.1111/nph.16544, figure 1)


## Study's location
* [Problem](https://github.com/BioSchemas/specifications/issues/556):
	studyLocation is preferred, but its domain is wrong and it doesn't extend contentLocation
* Proposed solution: 
	* use studyLocation, they're planning to fix it.
	* provisionally, add local defs to extend this from contentLocation 

## Study's contact
* [Problem](https://github.com/schemaorg/schemaorg/issues/3042):
  contactPoint's domain isn't right
* Proposed solution:
  * use it nonetheless
	* alternatively, if we don't want a conflict with Google validator, 
	  define agri:contactPoint as an extension of schema:maintainer and explain why.

## PropertyValue's types annotation
* [Problem](https://github.com/schemaorg/schemaorg/issues/2986)
  * additionalType to link ontology terms is very problematic, implies wrong entailments
* Proposed solution:
  * `dc:type`
  * from the discussions in the ticket mentioned above and from examples, propertyID is an identifier
	  of the **property type** (eg, "ISBN", "PubMed ID"), NOT a qualifier of the property **value**.
		Hence, we don't anything in schema.org for ontology term annotations.

## The case of a PVs having other PVs to define their type (eg, FactorValue/FactorType )
  * maybe valueReference, but I think is very confusing
	* `dc:type` is the other alternative.
	* possibly, add `additionalProperty` as well, so that it becomes visible to schema.org parsers
		* Currently the specs have very few types in the domain of `additionalProperty`, however the 
		  [Google validator](https://validator.schema.org/) accepts this property for `schema:Thing` 
	* possibly, open a ticket
	* decision: `dc:type` seems to be the clearest one, mention the option to use `additionalProperty` too.

## The case of property value and property type
* Eg, factor value vs factor type, experiment design as type only, protocol parameter value vs parameter name/type,
  observed value vs observed variable
* For the type, use (or extend() `schema:PropertyValue`, with the best practices:
  * `schema:name` to describe the category/type (eg, "experimental factor type", "protocol parameter type")
	  When you are extending schema:PropertyValue, this is redundant, only needed to ensure applications like Google
		get it
	* `schema:value` for the specific type (eg, "Treatment", "Watering")
* For the value, use (or extend) `schema:PropertyValue`
  * `schema:name` use the same or similar value used for its type (eg, "Treatment", "Treatment Type", "Factor Value[Treatment])
	  this is redundant when you're linking the type via `dc:type` (or a specific dedicated property), as explained above, 
		useful for the applications as mentioned above.
	* `schema:value` for the value (eg, "Nitrogen fertiliser", "Watered 2 times a day", "untreated")
* For details, see below (eg, FactorValue, FactorType, ExperimentalDesign)



## New type ExperimentalDesign
* The pattern below should be similar for type qualifiers
* extends schema:StructuredValue
* name is "study design description", optional
* value is a textual description
	* possibly have an additional longer `schema:description`, but don't omit `schema:value`
* propertyID to link ontology terms that identify the concept of experimental design
  * It should always have `ppeo:experimental_design`;
* possibly, dc:type for ontology linking of which a particular value is an instance, eg,
  * value = "factorial design with 2 factors", 
	* dc:type <http://purl.obolibrary.org/obo/OBI_0500015>
* links from study via new property `studyExperimentalDesign`?
  * this was proposed during the hackathon, but there is little point, search engines will 
	  recognise schema:additionalProperty, not this.



## New type ExperimentalFactorValue
* from PropertyValue
* ontology terms added as above
* links ExperimentalFactorType both via name and hasFactorType (a dc:type subprop, see below)

## New type ExperimentalFactorType
* this is optional, ExperimentalFactorValue already has a name for the type
* from PropertyValue, as in the case of ExperimentalDesign, use the same pattern
* FV/Type link is established via new prop **hasExperimentalFactorType**
	* a subproperty of dc:type, possibly additionalProperty too (see above)
* Likely, we want the symmetric **hasExperimentalFactorValue** too
* Study/Type link is established via new prop `studyFactorType`?
	* as for design, search engines will recognise `additionalProperty`

## Sample-related stuff
* After previous discussions, let's add these as subclasses of BioChemEntity
  * new class agri:FieldTrialBioMaterial. IMPORTANT: see notes below
  * new class agri:FieldTrialMaterialSource
  * new class agri:FieldTrialObservationUnit
	* Keep bioschema:BioSample, propose to see it as intangible, currently it mentions it 
	  should be material
* Specific relations involved in the above entities:
  * schema:subjectOf (or about) to be used to link BioChemEntity to bioschema:Study
	  (and consequently, the subclasses above).
	  * At the moment schema:partOf hasn't the right domain/range for this.
	* Possibly, open a ticket to ask for a serious review of mereological relationships 
	  (partOf, about, isRelatedTo, SKOS-like relations like broader, broaderInstantive, all of this is 
		either missing or poorly modelled in the current schema.org). Possibly, this would raise a big
		debate over radically different views about ontology engineering 
		(eg, https://github.com/schemaorg/schemaorg/issues/2984), or it would be dismissed as something
		it has already been discussed (and fought?) about. 
  * bioschema:isPartOfBioChemEntity to relate agri:FieldTrialBioMaterial to 
	  agri:FieldTrialMaterialSource 
	* Same relation to be used to relate bioschema:BioSample to agri:FieldTrialObservationUnit
		and this to agri:FieldTrialBioMaterial
	* possibly, let's introduce specific properties (derived from bioschema:isPartOfBioChemEntity):
		* agri:hasBioMaterial (domain Study, ObsUnit)
		* agri:hasMaterialSource (links FieldTrialBioMaterial/FieldTrialMaterialSource)
	* "Observation Unit Type" mapped to dc:type 
	

**Notes**: 
* Adding a super-class to group the ones above isn't worth, 
  BioChemEntity partOf Study should be enough.

* ISA maps ObsUnit to ISA:Sample and MIAPPE:Sample to ISA:Extract. IMHO it's wrong, unless, 
  * we want keep bioschema:BioSample as a generic sample class and then
	  subclass ObsUnit, Extract, StudyBioSource from bioschema:BioSample

* I can't fit agri:FieldTrialBioMaterial into more general types in schemas or BioSchemas, not in a 
  way that wouldn't be confusing to the MIAPPE community. That's because, from the point of view 
	of bioschemas, we should have:
	* MIAPPE:BiologicalMaterial, MIAPPE:MaterialSource, 
		MIAPPE:ObservationUnit and MIAPPE:BioSample as subclasses of *bioschema:BioSample*, 
	* new class bioschema:BioExtract to map MIAPPE:BioSample (as per ISA-Tab mapping)
	* new class bioschema:BioSource to map MIAPPE:BiologicalMaterial (as per ISA-Tab mapping)
	* a generic bioschema:BioChemEntity object to map MIAPPE:MaterialSource (with links to 
		bioschema:BioSource).
  

## Events and Protocols
* ISATab uses protocols for Events and growth protocol parameters for Environment
* It all sounds really weird, rainfall is fundamentally different from watering, in one case there is 
  something that happens in uncontrolled and unplanned way, in the other there is an intended action.

### Proposal
* Introduce bioschema:StudyEvent as subclass of schema:Action.
	This might map MIAPPE:Event OR you might want to be more specific with the 
	LabProtocol or StudyExternalEvent subclasses mentioned below
* Make bioschema:LabProtocol a subclass of bioschema:StudyEvent. Yes, it implies
	that LabProtocol is also an Action
	* According to documentation bioschema:bioSampleUsed can link generic bioschema:BioChemEntity, 
		not necessarily biosamples. So, this could be used to link the input material
	* Make bioschema:bioSampleUsed a subproperty of schema:object, in order to make it coherent
		with the upper Action model
* Using Action allows for using schema:result, with all events in the hierarchy, LabProtocol included
  Domain/range of object/result of a study event include observation unit, sample, data download
* Introduce bioschema:StudyExternalEvent, as a subclass of bioschema:StudyEvent and 
	distinct from LabProtocol
* Introduce bioschema:LabProtocolParameter as subclass of schema:PropertyValue
  and bioschema:hasProtocolParameter as subproperty of schema:additionalProperty
* Introduce bioschema:studyEventType with a range of text or URL or DefinedTerm or PropertyValue
  This will allow to define things like "growing protocol", "rainfall", "watering" and applies
	to both protocols and external events
* As above, schema:subjectOf links StudyEvent to Study (and hence, all the mentioned subclasses)


## Environment, Proposal
* Proposal: use an instance of LabProtocolParameter
* linked to Study, via additionalProperty (optional)
* linked to growth protocol, via hasProtocolParameter (optional)

## Cultural Practices
* one of the LabProtocolParameter(s) that can be associated to growth protocol

## Growth Facility
* a PropertyValue, name = "growth facility", propertyID = text about type and possibly URLs to 
  ontology terms.

## Map of experiment design
* as for Growth facility
* 


## Observed Variables

### StudyObservedVariable
* modelled in a way similar to ExperimentalFactorType
* from PropertyValue
* value/type link is established via new prop value **hasObservedVariable**
	* a subproperty of dc:type, possibly additionalProperty too (see above)
* Link to study via **studyObservedVariable**
* ontology terms defined as above

### StudyObservedValue
* from `PropertyValue`
* ontology terms added as above
* links variable via name and `hasObservedVariable` (which is subproperty of `dc:type`, see above)
* Can link `schema:DataDownload` via **hasObservedValue**. Can optionally link `bioschema:BioSample`, 
  `agri:FieldTrialObservationUnit`, via the same new property
  * NOT SURE at all we need this, additionalProperty would be enough.
	* An alternative to link from DataDownload is `schema:variableMeasured`, but this would require a domain addition
	  (to be asked to schema.org).
* for scale, use `schema:unitText` and/or `schema:unitCode`
* for trait, new property **observedValueTrait** as subproperty of `additionalProperty` (see above), 
  use PropertyValue to describe the trait
* for method, use `bioschema:measurementTechnique`, with `PropertyValue` or `LabProtocol` as possible targets
  * requires bioschema range extension
* for time scale, `additionalProperty` with `PropertyValue.name = "time scale"`
* TODO: consider schema:Observation

## StudyComputedValue subClassOf StudyObservedValue
* For instance, we might use this to represent the pvalue from an ANOVA analysis.
* A very uniform way to represent experiment results, including those that were derived/computed
* See example
* Considering it a form of observed value might be controversial
* See schema:Observation


## schema:DataDownload
* This is to represent MIAPPE:DataFile
* This is used to report data files associated to samples or observation units, or generically to the
  whole study
* `schema:subjectOf` (or the symmetric about) from these entities to DataDownload can be used for linking
* But `agri:evidence` is recommended when you want to make it explicit the entity that the data come from
  * In particular, `agri:evidence` is recommended from `DataDownload` to `bioschema:BioSample`
