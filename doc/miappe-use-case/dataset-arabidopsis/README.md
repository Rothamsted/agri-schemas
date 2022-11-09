
# Modelling of a MIAPPE/ISA-Tab use case
The notes below reports many discussion points and decisions made together with the  ELIXIR Plant Community. This document is an updated version of a [discusssion document](dataset-arabidopsis/discussion-biohack-2021.md) that emerged from the ELIXIR Biohackathon 2021 and 2022.

# Data Source

The real use case we have considered to test our modelling approach is based on:

*Optimizing experimental procedures for quantitative evaluation of crop plant performance in high throughput phenotyping systems*. 

* [DOI](https://doi.org/10.3389/fpls.2014.00770)
* [ISA-Tab files](http://dx.doi.org/10.5447/IPK/2014/4)

The experiment contains several measurement types, each having specific result types and data 
files.  

Here, we consider only the factors reported in the ISA-Tab, "soil cover" and "plant movement".

# The use case

In **[RDF/Turtle format](junker-2015-arabidopsis-miappe.ttl)**.  

**IMPORTANT**: see detailed explainations in the next section.


# Modelling choices

Most of the MIAPPE mapping work has been done within the ELIXIR plant community. Hereby, we 
describe some of the choices made.

## MIAPPE:Investigation
* `schema:Dataset` should be used to represent `MIAPPE:Investigation`, since this is the type that is most compatible with schema.org/bioschemas.
* It's recommended to add a qualifier like `schema:additionalType ppeo:investigation`

## Study
* Use `bioschema:Study` for this. Possibly use `schema:additionalType ppeo:study`, as above

* Study's location: use `schema:studyLocation` for this. Hoefully, [this issue](https://github.com/BioSchemas/specifications/issues/556) with it will be fixed at some point.

* Study's contact: use `schema:contactPoint` for this. Hopefully, [this issue](https://github.com/BioSchemas/specifications/issues/3402) with it will be fixed at some point.
  * **If you don't know if a study contributor is also a contact point**, use the more generic predicate `schema:contributor`.

* Use something like `bioschema:studyDomain <http://edamontology.org/topic_3810>` (agricultural science) to be compatible with the bioschema profile.

* Use something like `schema:studySubject <http://purl.obolibrary.org/obo/NCBITaxon_3702>` to be compatible with the bioschema profile (also, see notes below about subjectOf).

## Sample-related entities
* As you can see in the diagram above, we have defined subclasses of `schema:BioChemEntity`, which reflect the MIAPPE terminology:
* `agri:FieldTrialBioMaterial`
* `agri:FieldTrialMaterialSource`
* `agri:FieldTrialObservationUnit`
* `bioschema:BioSample` to represent a MIAPPE sample.

### Specific relations involved in the above entities:

* `schema:subjectOf` (or `schema:about`) to be used to link `BioChemEntity` to `bioschema:Study` (and consequently, the subclasses above).
	* `schema:studySubject` would be a more precise alternative and it's mentioned by the bioschemas study profile. However, its current domain/range (MedicalStudy) aren't suitable for plant biology, and this property seems to be specifically about the organism, plant, patient, etc that have been studied, while here, we are linking all the biochem entities that have been used for the purpose of studying one of them (eg, a plant variety). 
* Another alternative might be `schema:partOf`, but currently it hasn't the right domain/range for this, and it seems there is a peculiar view on schema.org community about these generic mereological relationships ([example](https://github.com/schemaorg/schemaorg/issues/2984).  

* Use `bioschema:isPartOfBioChemEntity` (or `hasBioChemEntityPart`) to relate `agri:FieldTrialBioMaterial` from (or to) `agri:FieldTrialMaterialSource` (as per bioschemas profile)
* Same relation to be used to relate `bioschema:BioSample` to `agri:FieldTrialObservationUnit`, and this to `agri:FieldTrialBioMaterial`
* We don't see such a need to introduce specific properties for this (like `agri:hasBioMaterial`, `agri:hasMaterialSource`).
* Use `dc:type` in `agri:FieldTrialObservationUnit` for MIAPPE:"Observation Unit Type"
	
* We considered a specific a super-class to group the ones introduced above, we gave up with this, since this class wouldn't add much to `schema:BioChemEntity`.
  * See [details here](dataset-arabidopsis/discussion-biohack-2021.md) about other alternatives we have considered, before reaching consensus on the modelling described above.

## Value/Type Pairs

### PropertyValue's types annotation
* Use `dc:type` to qualify **the value** of a name/value pair. For instance, attach `dc:type <http://purl.obolibrary.org/obo/NCBITaxon_3702>` to a `schema:PropertyValue` instance with name: "organism" and value "arabidopsis."
* In general, don't use `schema:additionalType` for informal qualifier, since this property is much more committing, as [explained here](https://github.com/schemaorg/schemaorg/issues/2986).
* When you want to **qualify the type of a PV**, prefer `schema:propertyID`. For instance: name: "p-value", `propertyID: sio:SIO_000765`, value: 0.01. This is the purpose propertyID is designed for.

To clarify the type qualifier further, consider this:

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

As said above, this property is not exactly an instance of day, and linking the ontology annotations via something that implies `rdf:type` would also lead to the property being in the intersection of 'day' and 'aleurone layer', which might be disjoint classes and hence the fragment above would lead to an inconsistency.  

Similarly, `schema:propertyID <aleurone layer>` wouldn't be correct, cause we are not giving a value for the aleurone layer property, rather, we're defining something that is loosely a subclass of that (note that `skos:narrowerInstantive` might be more precise than `dc:type`, we prefer the latter for sake of simplicity).  

### Specific type-like properties,
* In certain cases, we define specific value/type properties, such as `agri:hasExperimentalFactorType` (see below). We do this when we want to be explicit on the kind of instantive relation we are representing, mostly to reflect the terminology used in the application domain.
* When we introduce these new properties, they're defined as subproperties of `dc:type`.


### PV extensions that have a value/type relationship (eg, ExperimentalFactorValue/ExperimentalFactorType )
* The following sections apply to cases like factor value vs factor type, experiment design 
  (as type only), protocol parameter value vs parameter name/type, observed value vs observed variable. They're similar cases in the structural sense: essentially, they're all value/type pairs, and they all have similar properties, such as name, specific value, ontology term annotations. This is similar to other formats, such as ISA-Tab, MAGE-Tab, etc.
* As said above, in a number of cases (see below), we want/need to introduce new types, for a number of
  reasons, eg, they're part of the common terminology, they're needed qualifiers.
* As outlined above, we chose to relate them via `dc:type`, eg, 
  ```javascript
	ex:nitrogenHigh a agri:ExperimentalFactorValue;
	  schema:name "Nitrogen, High Concentration";
		schema:value "High Concentration";
		dc:type ex:fertilizer;
	.

	ex:fertilizer a agri:ExperimentalFactorType
		schema:name "Experimental Factor Type";
		schema:value "Fertilizer Type";
	.
	```
  * both `agri:ExperimentalFactorValue` and `agri:ExperimentalFactorType` are defined as subclasses 
	  of `schema:PropertyValue`
* until new terms like ExperimentalFactorValue aren't accepted by schema.org (and aren't parsed by tools like the [Google validator](https://validator.schema.org/)), it is advisable to define these type instances by adding `schema:PropertyValue` as their class (eg, `ex:nitrogenHigh a agri:ExperimentalFactorValue, schema:PropertyValue`. This is redundant, but it can help with interoperability.
* Note that, according to the above `dc:type` can be used for both generic links to the URIs of external ontology terms (see the previous section) and for linking local PV types, as ghe case presented here. It's easy (in SPARQL or alike) to distinguish between the two cases (`?pval dc:type ?ptype. ?ptype a agri:ExperimentalFactorType`). The case of a generic ontology term can possibly be made clearer by using `schema:DefinedTerm`, eg
	```javascript
	ex:sampleProp a agri:ExperimentalFactorValue, schema:PropertyValue;
	  schema:name "aleurone layer";
		dc:type <http://purl.obolibrary.org/obo/PO_0005360>, ex:plantPart.

	<http://purl.obolibrary.org/obo/PO_0005360> a schema:DefinedTerm.
	```

### Details about value/type cases
For the property values used as types (eg, factor type), use and/or extend `schema:PropertyValue`, as said above. Then:
* Use `schema:name` to describe the category/type (eg, "experimental factor type", "protocol parameter type"). 
* When you are using a specific extension of `schema:PropertyValue`, eg, `ExperimentalFactorType`, this is redundant (the new type says the same thing the name says), yet it might be useful for visualisation/UI purposes and to ensure applications like Google get the data.
* Use `schema:value` for the specific type (eg, "Treatment", "Watering")


For the PVs used as values (of a type PV), use or extend `schema:PropertyValue` too, as above, and then:
* use `schema:name` use the same or similar value used for its type (eg, "Treatment", 
  "Treatment Type", "Factor Value[Treatment])
* Again, this is redundant when you're linking the type via `dc:type` as explained above, 
	but might be useful.
* USe `schema:value` for the value (eg, "Nitrogen fertiliser", "Watered 2 times a day", "untreated")

For details, see below (eg, ExperimentalFactorValue, ExperimentalFactorType, ExperimentalDesign).


## New type agri:ExperimentalDesign
The following applies what said above for value/type pairs.
* extends `schema:PropertyValue`
* `schema:name` is "study design", and it's optional
* `schema:value` is a short textual description of the experimental design (summary or title)
* `schema:description` maps MIAPPE's `study design description`
  * Optionally, the description could be duped into `schema:value` (to support common practice
	  with schema.org)
* `schema:propertyID` should have `ppeo:experimental_design` among its values, ie, to represent the
  concept that the property is about the design type. Again, this is redundat, yet useful
  * TODO: an alternative is that we propose ExperimentalDesign as a new term and that it
	  subclasses `ppeo:experimental_design` (and PV)
* possibly, `dc:type` for ontology linking of which a particular value is an instance, eg,
  * `schema:value "factorial design with 2 factors"`, 
	* `dc:type <http://purl.obolibrary.org/obo/OBI_0500015>`
* links from study via new property `studyExperimentalDesign`?
  * this was proposed during the hackathon, but there is little point, search engines will 
	  recognise `schema:additionalProperty` only, not this. We have used `additionalProperty` in our
		use case.

## New type ExperimentalFactorValue
* As above, this is an extension of PropertyValue
* ontology terms added as above, using dc:type
* we introduce `agri:hasExperimentalFactorType` to link to the type.
* we also introduce the symmetrical property `agri:hasExperimentalFactorValue`, so that there is
  an easy way to list all the possible factor values for a type.
	* Both `ExperimentalFactorType` and `Study` (or schema:Thing?) should be in the range of this 
	  property, so that we can qualify the factor values and types an entity is about

## New type ExperimentalFactorType
* this is optional, ExperimentalFactorValue already can accomodate  a type qualifier in
  its name. However, we expect it to be used in most cases (as per common practices)
* extends `PropertyValue`, as explained above
* Study/Type link is established via additionalProperty (see the discussion about the 
  experimental design above)


## Events and Protocols

ISATab uses protocols for Events and growth protocol parameters for Environment. It all sounds 
really weird, rainfall is fundamentally different from watering, in one case there is something 
that happens in uncontrolled and unplanned way, in the other there is an intended action.  

So, our proposal is as follow.

* We propose the new `agri:StudyEvent` as subclass of `schema:Action`.
	This maps `MIAPPE:Event` generically, OR, possibly, we have more specific subclsasses:
* `bioschema:LabProtocol` is made a subclass of `bioschema:StudyEvent`. Yes, it implies
	that LabProtocol is also an Action
	* According to documentation, `bioschema:bioSampleUsed` can link generic 
	`bioschema:BioChemEntity`, not necessarily biosamples. So, this could be used to link the input 
	material of a lab protocol
	* `bioschema:bioSampleUsed` is made a subproperty of `schema:object`, in order to make it coherent
		with the upper model given for the Action class. Until this is 
* Using Action allows for using `schema:result`, with all subclasses in the hierarchy, `LabProtocol` 
  included
* Domain/range of object/result of a study event include observation unit, sample, data download
* We propose the new `bioschema:StudyExternalEvent`, as a subclass of `bioschema:StudyEvent` and 
	distinct from `LabProtocol`
* Introduce `agri:studyEventType` at the StudyEvent level, with a range of text or URL or DefinedTerm or PropertyValue
  This will allow to define things like "growing protocol", "rainfall", "watering" and applies
	to both protocols and external events
* As elsewhere, `schema:subjectOf` links `StudyEvent` to `Study` (and hence, all the mentioned subclasses)
	* As said above prefer this to `schema:partOf`. `schema:studySubject` has a very different meaning.

### LabProtocolParameterValue and LabProtocolParameterType

* We propose the new `agri:LabProtocolParameterValue` as subclass of `schema:PropertyValue`.
  Similarly, introduce `agri:LabProtocolParameterType` (both modelled as per the discussion above on value/type pairs).
* introduce `agri:hasProtocolParameter` as subproperty of `schema:additionalProperty`
  (to link a protocol to its parameter values or types)

## Observed Variables

### New proposal: agri:StudyObservedVariable
* modelled in a way similar to `ExperimentalFactorType` (and, again, like value/type pair)
* So, it extends `PropertyValue`, ontology term annotations are added as above
* Possibly the link from study is established via a new property like `agri:studyObservedVariable`
  * currently, we use `schema:additionalProperty`

### New proposal: agri:StudyObservedValue
* Another value/type case. 
* extends `PropertyValue`, ontology terms added as above
* * Links StudyObservedVariable via `agri:hasObservedVariable`
	* a subproperty of `dc:type`, as above
* Use `schema:additionalProperty` to link to this from `schema:DataDownload`, `bioschema:BioSample`, `agri:FieldTrialObservationUnit`.
	* We haven't decided if to add something like `agri:hasObservedValue` for this.
* TODO: an alternative to link from DataDownload is `schema:variableMeasured`, but this would require 
	a domain addition (to be asked to schema.org).
* for MIAPPE/scale, use `schema:unitText` and/or `schema:unitCode`
* for MIAPPE/trait, new property `hasObservedValueTrait` as subproperty of `additionalProperty` 
  (see above), use PropertyValue to describe the trait
* for method, use `bioschema:measurementTechnique`, with `PropertyValue` or `LabProtocol` as 
  possible targets
  * requires bioschema range extension
* for time scale, `schema:additionalProperty` with `PropertyValue.name = "time scale"`
* We have considered `schema:Observation` for this StudyObservedValue, but currently, it has very different assumptions and objectives

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
* This is to represent `MIAPPE:DataFile` (use this qualifier with additionalType)
* It's is used to report data files associated to samples or observation units, or generically to 
  the whole study
* Use `agri:evidence` to link data to entities like samples or studies
  * An alternative for this would be `schema:subjectOf` (or the symmetric `schema:about`). But the new evidence property is more explicit. Possibly, add these schema annotations too, for interoperability.

## MIAPPE Environment, Proposal
* Proposal: use an instance of `agri:LabProtocolParameter`
* linked to Study, via `additionalProperty` (optional)
* linked to growth protocol, via `agri:hasProtocolParameter` (optional)

## Cultural Practices
* one of the `LabProtocolParameter`(s) that can be associated to growth protocol

## Growth Facility
* an `agri:LabProtocol` of type "Growth Protocol"
* Growth facility is a `LabProtocolParameterValue`, linked to this protocol
* with `schema:propertyID ppeo:growth_facility`
* `schema:name "growth facility"`
* `schema:value` for the short name/title, if any 
* `schema:description` for "description of growth facility" (similarly to ExperimentalDesign above)

## Map of experiment design
* as for Growth facility or ExperimentalDesign
