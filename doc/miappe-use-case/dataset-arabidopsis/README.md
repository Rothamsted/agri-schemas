
# Modelling of a MIAPPE/ISA-Tab use case
The notes below reports many discussion points and decisions made together with the 
ELIXIR Plant Community. 

A summary of the MIAPPE/*Schemas mappings described below is here (TODO)

# Data Source

The example below is based on:

*Optimizing experimental procedures for quantitative evaluation of crop plant performance in high throughput phenotyping systems*. 

* [DOI](https://doi.org/10.3389/fpls.2014.00770)
* [ISA-Tab files](http://dx.doi.org/10.5447/IPK/2014/4)

The experiment contains several measurement types, each having specific result types and data 
files.  

Here, we consider only the factors reported in the ISA-Tab, "soil cover" and "plant movement".

# The use case

In **[RDF/Turtle format](junker-2015-arabidopsis-miappe.ttl)**.  

**IMPORTANT**: see detailed explainations in the next section.


# Modelling choices (TODO: PROVISIONAL, TO BE REVIEWED)

Most of the MIAPPE mapping work has been done within the ELIXIR plant community. Hereby, we 
describe some of the choices made.

## MIAPPE:Investigation
* We propose to introduce `agri:FieldTrialInvestigation` as a subclass of `schema:Dataset`
* This is to reconcile the hackathon discussions, where it was clarified that Investigation is 
  intended as dataset with the MIAPPE publication, where... TODO:what does it say? 
	(https://nph.onlinelibrary.wiley.com/doi/10.1111/nph.16544, figure 1)

## Study's location
* [Problem](https://github.com/BioSchemas/specifications/issues/556):
	`studyLocation` is preferred, but its domain is wrong and it doesn't extend `contentLocation`
* Proposed solution: 
	* use `studyLocation`, they're planning to fix it
	* provisionally, add local extensions to bioschemas, to extend this from `contentLocation` 

## Study's contact
* [Problem](https://github.com/schemaorg/schemaorg/issues/3042):
  `schema:contactPoint`'s domain isn't right
* Proposed solution:
  * use it nonetheless
	* alternatively, if we don't want a conflict with Google validator, 
	  define `agri:contactPoint` as an extension of `schema:maintainer` and explain why
	* In the use case, we used `schema:contactPoint`
	* Also note that we used `schema:contributor` for cases where we're not sure if someone
	  is also a reference contact


## Sample-related stuff
* After previous discussions, let's add the following as subclasses of `schema:BioChemEntity`:
* new class `agri:FieldTrialBioMaterial`. IMPORTANT: see notes below
* new class `agri:FieldTrialMaterialSource`
* new class `agri:FieldTrialObservationUnit`
* Keep `bioschema:BioSample`, we propose to see it as an intangible entity (eg a questionnaire 
  answer set is a kind of sample in a psychology experiment), current specifications mention it 
	should be material (TODO: Bioschemas ticket?)

### Specific relations involved in the above entities:
* `schema:subjectOf` (or `schema:about`) to be used to link BioChemEntity to `bioschema:Study`
	(and consequently, the subclasses above).
	* TODO: `schema:studySubject` would be a more precise alternative and it's mentioned by the
	  bioschemas study profile, however neither its current domain (MedicalStudy) nor its range (MedicalEntity) are 
		suitable for plant biology. 
* At the moment `schema:partOf` hasn't the right domain/range for this.
* TODO: Possibly, open a ticket to ask for a serious review of mereological relationships 
	(partOf, about, isRelatedTo, SKOS-like relations like broader, broaderInstantive, all of this is 
	either missing or poorly modelled in the current schema.org).
* Possibly, this would raise a big debate over radically different views about ontology engineering 
	([example](https://github.com/schemaorg/schemaorg/issues/2984)), or it would be dismissed as 
	something it has already been discussed (and fought?) about. 
* Use `bioschema:isPartOfBioChemEntity` (or hasBioChemEntityPart) to relate `agri:FieldTrialBioMaterial` from (or to)
	`agri:FieldTrialMaterialSource` (as per bioschemas profile)
* Same relation to be used to relate `bioschema:BioSample` to `agri:FieldTrialObservationUnit`
	and this to `agri:FieldTrialBioMaterial`
* possibly, let's introduce specific properties (derived from `bioschema:isPartOfBioChemEntity`):
	* `agri:hasBioMaterial` (domain Study, ObsUnit)
	* `agri:hasMaterialSource` (links FieldTrialBioMaterial/FieldTrialMaterialSource)
* "Observation Unit Type" mapped to dc:type 
	

**Notes** (by M. Brandizi):  

* Adding a super-class to group the ones introduced above isn't worth, 
  BioChemEntity should be enough.
* ISA maps ObsUnit to ISA:Sample and MIAPPE:Sample to ISA:Extract. IMHO it's wrong, unless, 
  * we want keep `bioschema:BioSample` as a generic sample class and then
	  subclass ObsUnit, Extract, StudyBioSource from `bioschema:BioSample`
* I can't fit `agri:FieldTrialBioMaterial` into more general types in schemas or BioSchemas, 
  not in a way that wouldn't be confusing to the MIAPPE community. That's because, from the point of view of bioschemas, we should have:
	* MIAPPE:BiologicalMaterial, MIAPPE:MaterialSource, 
		MIAPPE:ObservationUnit and MIAPPE:BioSample as *subclasses of bioschema:BioSample*, 
	* new class bioschema:BioExtract to map MIAPPE:BioSample (as per ISA-Tab mapping)
	* new class bioschema:BioSource to map MIAPPE:BiologicalMaterial (as per ISA-Tab mapping)
	* a generic bioschema:BioChemEntity object to map MIAPPE:MaterialSource (with links to 
		bioschema:BioSource).
* So, given all of the above, the solution proposed is one with a minimal impact on both
  (bio)schema and MIAPPE

## Value/Type Pairs

### PropertyValue's types annotation
* [Problem](https://github.com/schemaorg/schemaorg/issues/2986):
  * `schema:additionalType` to link ontology terms to a property value is very problematic, cause 
	  it might easily imply wrong entailments (due to the fact it extends `rdf:type`), especially 
		when additional types are inferred via text mining or ontology annotator tools.
* Proposed solution:
  * `dc:type`
	* we considered `schema:propertyID`, however, from the discussions in the ticket mentioned above 
		and from examples, that is an identifier of the **property type** (eg, "ISBN", "PubMed ID"), 
		NOT a qualifier of the property **value**. Hence, we don't anything in schema.org for ontology 
		term annotations. `dc:type` is the next best vocabulary we can think of for this case.
* Example (from the GXA use case):
	```javascript
	ex:sample_prop a schema:PropertyValue; 
		schema:name "14 day post anthesis, aleurone layer";
		# These can come from eg, manual curation or auto-annotation
		# (of course multiple terms are possible)
		dc:type
			<http://purl.obolibrary.org/obo/PO_0005360>, # aleurone layer
			<http://www.cropontology.org/rdf/CO_321:0000434>; # day 
	.
	```
  * As said above, this property is not exactly an instance of day, and linking the ontology 
	  annotations via something that implies `rdf:type` would also lead to the property being 
		in the intersection of 'day' and 'aleurone layer', which might be disjoint classes and hence
		the fragment above would lead to an inconsistency.
	* Similarly, `schema:propertyID <aleurone layer>` wouldn't be correct, cause we are not giving
	  a value for the aleurone layer property, rather, we're defining something that is loosely
		a subclass of that (note that `skos:narrowerInstantive` might be more precise than `dc:type`, 
		we prefer the latter for sake of simplicity).
* possibly, let's open a(nother) ticket on schema.org, to report that they haven't anything for
  this relation (mention `skos:narrowerIntantive` as above)

### Specific type-like properties,
* In certain cases, we define specific value/type properties, such as 
  `agri:hasExperimentalFactorType` (see below). We do this when we want to be explicit 
	on the kind of instantive relation we are representing, mostly to reflect the terminology
	used in the application domain.
* When we introduce these new properties, they're defined ad subproperties of `dc:type`.


### PV extensions that have a value/type relationship (eg, ExperimentalFactorValue/ExperimentalFactorType )
* The following sections apply to cases like factor value vs type, experiment design 
  (as type only), protocol parameter value vs parameter name/type, observed value vs observed variable. They're similar cases in the structural sense: essentially, they're all 
	value/type pairs, and they all have similar properties, such as name, specific value, 
	ontology term annotations, this is similar to other formats, such as ISA-Tab, MAGE-Tab,
  etc.
* In a number of cases (see below), we want/need to introduce new types, for a number of
  reasons, eg, they're part of the common terminology, they're needed qualifiers.
* As outlined above, we chose to relate them via `dc:type`, eg, 
  ```javascript
	ex:nitrogen a agri:ExperimentalFactorValue;
	  schema:name "Nitrogen, High Concentration";
		dc:type ex:fertilizer;
	.

	ex:fertilizer a agri:ExperimentalFactorType
		schema:name "Experimental Factor Type";
		schema:value "Fertilizer Type";
	.
	```
  * both `agri:ExperimentalFactorValue` and `agri:ExperimentalFactorType` are defined as subclasses 
	  of `schema:PropertyValue`
* until new terms like ExperimentalFactorValue aren't accepted by schema.org (and aren't parsed 
  by tools like the [Google validator](https://validator.schema.org/)), it is advisable to define 
	these type instances by adding `schema:PropertyValue` as their class (eg, 
	`ex:nitrogen a agri:ExperimentalFactorValue, schema:PropertyValue`. This is redundant, but 
	it can help interoperability.
* we considered `schema:valueReference` as a possible value/type link in place of dc:type, 
  but that appears very counter-intuitive and confusing
* Note that `dc:type` can be used for both generic links to the URIs of external ontology terms
  (see the previous section) and for the case at issue. It's easy (in SPARQL or alike) to 
	distinguish between the two cases (`?pval dc:type ?ptype. ?ptype a agri:ExperimentalFactorType`).
  The case of a generic ontology term can possibly be made clearer by using `schema:DefinedTerm`:
	```javascript
	ex:sample_prop a agri:ExperimentalFactorValue, schema:PropertyValue;
	  schema:name "aleurone layer";
		dc:type <http://purl.obolibrary.org/obo/PO_0005360>, ex:plantPart.

	<http://purl.obolibrary.org/obo/PO_0005360> a schema:DefinedTerm.

  ex:plantPart a agri:ExperimentalFactorType, schema:PropertyValue;
	  schema:name "Factor Value Type";
		schema:value "Collected Plant Part";
	.
	```

### Details about value/type cases
For the type, use and/or extend `schema:PropertyValue`, as said above. Then:

* Use `schema:name` to describe the category/type (eg, "experimental factor type", "protocol parameter type"). 
* When you are extending `schema:PropertyValue`, this is redundant, yet it might be useful for
  visualisation/UI purposes and to ensure applications like Google get the data.
* Use `schema:value` for the specific type (eg, "Treatment", "Watering")


For the value, use or extend `schema:PropertyValue` too, as above, and then:

* use `schema:name` use the same or similar value used for its type (eg, "Treatment", 
  "Treatment Type", "Factor Value[Treatment])
* Again, this is redundant when you're linking the type via `dc:type` as explained above, 
	but might be useful.
* USe `schema:value` for the value (eg, "Nitrogen fertiliser", "Watered 2 times a day", "untreated")

For details, see below (eg, ExperimentalFactorValue, ExperimentalFactorType, ExperimentalDesign).


## New type agri:ExperimentalDesign
The follow applies what said above for value/type pairs.
* extends `schema:PropertyValue`
* `schema:name` is "study design", and it's optional
* `schema:value` is a short textual description of the experimental design (summary or title)
* `schema:description` maps MIAPPE's `study design description`
  * Optionally, the description could be duped into `schema:value` (to support common practice
	  with schema.org)
* `schema:propertyID` to link ontology terms that identify the concept of experimental design,
   for the specific design (eg, "treatment/control design"), use `dc:type` as explained above
* `schema:propertyID` should have `ppeo:experimental_design` among its values;
  * TODO: an alternative is that we propose ExperimentalDesign as a new term and that it
	  subclasses `ppeo:experimental_design`
* possibly, `dc:type` for ontology linking of which a particular value is an instance, eg,
  * `schema:value "factorial design with 2 factors"`, 
	* `dc:type <http://purl.obolibrary.org/obo/OBI_0500015>`
* links from study via new property `studyExperimentalDesign`?
  * this was proposed during the hackathon, but there is little point, search engines will 
	  recognise schema:additionalProperty, not this. We have used additionalProperty in our
		use case.

## New type ExperimentalFactorValue
* As above, this is an extension of PropertyValue
* ontology terms added as above, using dc:type
* we introduce `agri:hasExperimentalFactorType` to link to the type.
* we also introduce the symmetrical property `agri:hasExperimentalFactorValue`, so that there is
  an easy way to list all the possible factor values for a type.
	* Both ExperimentalFactorType and Study (or schema:Thing?) should be in the range of this 
	  property, so that we can qualify the factor values and types an entity is about

## New type ExperimentalFactorType
* this is optional, ExperimentalFactorValue already can accomodate  a type qualifier in
  its name. However, we expect it to be used in most cases (as per common practices)
* extends PropertyValue, as explained above
* Study/Type link is established via additionalProperty (see the discussion about the 
  experimental design above)



## Events and Protocols

ISATab uses protocols for Events and growth protocol parameters for Environment. It all sounds 
really weird, rainfall is fundamentally different from watering, in one case there is something 
that happens in uncontrolled and unplanned way, in the other there is an intended action.  

So, our proposal is as follow.

* Introduce `agri:StudyEvent` as subclass of `schema:Action`.
	This might map MIAPPE:Event OR you might want to be more specific with the 
	`LabProtocol` or `StudyExternalEvent` subclasses mentioned below
* Make `bioschema:LabProtocol` a subclass of `bioschema:StudyEvent`. Yes, it implies
	that LabProtocol is also an Action
	* According to documentation, `bioschema:bioSampleUsed` can link generic 
	`bioschema:BioChemEntity`, not necessarily biosamples. So, this could be used to link the input 
	material of a lab protocol
	* Make `bioschema:bioSampleUsed` a subproperty of `schema:object`, in order to make it coherent
		with the upper model given for the Action class
* Using Action allows for using `schema:result`, with all subclasses in the hierarchy, LabProtocol 
  included
* Domain/range of object/result of a study event include observation unit, sample, data download
* Introduce `bioschema:StudyExternalEvent`, as a subclass of `bioschema:StudyEvent` and 
	distinct from LabProtocol
* Introduce `agri:studyEventType` at the StudyEvent level, with a range of text or URL or DefinedTerm or PropertyValue
  This will allow to define things like "growing protocol", "rainfall", "watering" and applies
	to both protocols and external events
* As elsewhere, `schema:subjectOf` links StudyEvent to Study (and hence, all the mentioned subclasses)
	* TODO: `schema:partOf` or `schema:studySubject` would be more appropriate, but neither have the right 
	  domain or range.

### LabProtocolParameterValue and LabProtocolParameterType

* Introduce `agri:LabProtocolParameterValue` as subclass of `schema:PropertyValue`.
  Similarly, introduce `agri:LabProtocolParameterValue` (both modelled as per the discussion above on value/type pairs).
	* TODO: do we need hasProtocolParameterType, or is `dc:type` enough?
* introduce `agri:hasProtocolParameter` as subproperty of `schema:additionalProperty`
  (to link a protocol to its parameter values or types)

## Observed Variables

### New proposal: agri:StudyObservedVariable
* modelled in a way similar to ExperimentalFactorType (and, again, like value/type pair)
* So, it extends PropertyValue, ontology term annotations are added as above
* Possibly the link from study is established via a new property like `agri:studyObservedVariable`
  * currently, we use `schema:additionalProperty`

### New proposal: agri:StudyObservedValue
* A value/type case. 
* extends `PropertyValue`, ontology terms added as above
* * Links StudyObservedVariable via `agri:hasObservedVariable`
	* a subproperty of `dc:type`, as above
* Can link `schema:DataDownload` via `agri:hasObservedValue`. Optionally, this can also link 
  `bioschema:BioSample`, `agri:FieldTrialObservationUnit` to an obs value
  * TODO: not sure at all we need this, additionalProperty would be enough (currently, we do this in the 
	  use case).
	* TODO: an alternative to link from DataDownload is `schema:variableMeasured`, but this would require 
	  a domain addition (to be asked to schema.org).
* for MIAPPE/scale, use `schema:unitText` and/or `schema:unitCode`
* for MIAPPE/trait, new property `hasObservedValueTrait` as subproperty of `additionalProperty` 
  (see above), use PropertyValue to describe the trait
* for method, use `bioschema:measurementTechnique`, with `PropertyValue` or `LabProtocol` as 
  possible targets
  * requires bioschema range extension
* for time scale, `schema:additionalProperty` with `PropertyValue.name = "time scale"`
* TODO: consider `schema:Observation`, currently it has very different assumptions
  and objectives

## New proposal: agri:StudyComputedValue subClassOf agri:StudyObservedValue
* To be used for anything that is computed from data, in particular, from observed
  values
* Examples: 
  * average yield
	* p-value from a t-student test over mean yield difference
	* p-value from some ANOVA analysis of gene expression levels.
* This would be a simple and very uniform way to represent experiment results, including 
  those that were derived/computed
* See MIAPPE use  case, TODO: gene expression use case to be aligned to this
* Considering it a form of observed value (ie, a subclass of it) might be controversial
* As mentioned above, we might want to consider `schema:Observation`

## New proposal, agri:StudyComputedVariable subClassOf agri:ObservedVariable
* Just as above, it is the counterpart of computed value

## schema:DataDownload
* This is to represent MIAPPE:DataFile
* It's is used to report data files associated to samples or observation units, or generically to 
  the whole study
* `schema:subjectOf` (or the symmetric `schema:about`) from these entities to DataDownload 
  can be used for linking
* But `agri:evidence` might be more appropriate when you want to make the entity that 
  the data come from explicit
  * In particular, `agri:evidence` is recommended from `DataDownload` to `bioschema:BioSample`

## MIAPPE Environment, Proposal
* Proposal: use an instance of `agri:LabProtocolParameter`
* linked to Study, via additionalProperty (optional)
* linked to growth protocol, via `agri:hasProtocolParameter` (optional)

## Cultural Practices
* one of the LabProtocolParameter(s) that can be associated to growth protocol

## Growth Facility
* There is a LabProtocol of type "LabProtocol"
* Growth facility is a LabProtocolParameterValue
* with `schema:propertyID ppeo:growth_facility`
* `schema:name "growth facility"`
* `schema:value` for the short name/title, if any 
* `schema:description` for "description of growth facility" (similarly to ExperimentalDesign above)

## Map of experiment design
* as for Growth facility or ExperimentalDesign
