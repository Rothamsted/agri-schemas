# Modelling Agri-Schemas

This is a (for the moment draft) project to model linked data schemas (ie, lightweight ontologies for the fields of agriculture, food, agri-business, plant biology.

The work leverages mainly [schema.org](https://schema.org/) and [bioschemas](https://bioschemas.org/). As in those projects, we aim at very simple and practical modelling, which can be useful to share data in an interoperable way, especially by means of APIs and annotated web pages.

The work was born within the [Design Future Wheat](https://designingfuturewheat.org.uk/) project, and for the moment it's focused on the use cases dealt with in it. In fact, so far we have been building our schemas starting from well known use cases within crop improvement research. There have been two DFW hackathons where we have done most of the work so far.

## Use cases

This work has started with a first DFW hackathon in 2018, where we first [outlined the possible 
types](https://docs.google.com/document/d/15yMoJDvVEE-mDQgIUY-l1foTb35Qp_qsMIgReyP5VoQ/edit) (ie, 
classes, properties/relations) that we might need in DFW-relevant data.

Leveraging that, we have started considering use cases from real data, and we have started 
modelling them using existing schemas. At the same time, we have started to [propose new types](agri-schema.ttl) as needed.

These are the use cases considered:

  * [Molecular Biology, pathways/genes/proteins](biomol-use-case.ttl) (from Knetminer)
  * [Molecular Biology, ontology terms](ontology-use-case.ttl) (from Knetminer)
  * [Molecular Biology, host-pathogen interactions](phi-base-use-case.ttl) (PHI-Base)
  * Dataset description, TODO (based on `bioschema:Dataset`, but CKAN might need DCAT, VoID is also worth to consider)
  * Field trials
    * [MIAPPE and ISA-Tab for phenotyping](miappe-use-case), [MIAPPE use case](miappe-use-case.ttl)
    * [AHDB](ahdb-use-case.md)
  * Links between [field trials, cultivars and genes](trials-genes.md)
    * Includes the [EBI Gene Expression Atlas use case](ebi-gxa-use-case/README.md)
  * [Weather conditions and forecasts](weather-use-case.md)

## General Modelling Principles

The modelling above is being based on the following principles.

### Leverage primarily on schema.org and bioschemas 

New classes and properties should be based on these lightweight ontologies. When a type in them is good enough for our use case, use it directly. We also recommend the following principles about these two references:

  * Possibly, use the same [profiling principle](https://bioschemas.gitbook.io/training-portal/) used in bioschemas.  

  * Use constructs like [domainIncludes](https://schema.org/domainIncludes) and [rangeIncludes](https://schema.org/rangeIncludes) to define new types. This is lighter/simpler than OWL (can be possibly converted to OWL statements) and fits into the schema/bioschemas model.  

  * Don't use `owl:datatypeProperty/owl:objectProperty`. All schema.org properties are simple instances of `rdf:Property`. In our files, we instantiate `owl:AnnotationProperty` too, but just for the practical reason that Protegé doesn't see anything that isn't under the OWL vocabulary.  

  * The above also allows you to use properties and classes in a simple way. For instance, the
  values for the property `agri:accession` can be either a simple string (eg, `"GO:00000297"`), 
  or a [`StructuredValue`](https://schema.org/StructuredValue), which is able to further eference 
  elements like an [`url`](https://schema.org/url)
  or [`dc:source`](http://purl.org/dc/elements/1.1/source) (which also avoids us to be concerned 
  of the distinction between [dc: and dc:terms](https://stackoverflow.com/questions/47519315)).  

  * Before considering using more comples types, use the simplest/more general. For instance, an 
  [`additionalType`](https://schema.org/additionalType) attached to a [biological sample](https://bioschemas.org/types/Sample/) resource is usually enough to say which organisms the sample is instance of. Similarly, a [`PropertyValue`](https://schema.org/PropertyValue) instance might be good to track very dataset-specific properties (eg, see the [PHI-base use case](drafts/201904-dfw-hackathon/phi-base-use-case.ttl)).


### List of additional preferred schemas/ontologies

Try to reuse existing types as much as possible. When you feel you need a new definition, use schema or bischemas, as said above. When your use case don't fit in them, try the following common schemes/ontologies (in the listed order), before creating a new definition: 

* Dublin Core Elements (as said above, we don't quite need terms)
* RDF-S
* SKOS (but first consider [DefinedTerm](https://schema.org/DefinedTerm) and see the discussion about term annotations).
* [Annotation Ontology](https://www.w3.org/TR/annotation-vocab/)

When introducing a new term, try as much as possible to find appropriate existing terms to extend 
(`rdfs:subClassOf/rdfs:subPropertyOf`). If a new term is defined, try to provide minimal mapping 
to external ontologies (eg, [SIO](https://bioportal.bioontology.org/ontologies/SIO)). We say 
"minimal" because furter mappings should go in separated files and addressed after initial 
modelling.  

The best ways to refer an external term are `rdfs:subClassOf`, `rdfs:subPropertyOf` 
(beware they require a strong formal commitment),  `schema:additionalType` (when there is a more 
informal link, eg, between [`bioschema:LabProtocol`](http://bioschemas.org/LabProtocol) and 
[`obi:protocol`](http://purl.obolibrary.org/obo/OBI_0000272)) or `rdfs:seeAlso` (for cross-type 
links and similarly informal relations, eg, see `agri:isBiologicallyRelatedTo` in [agri-schema definitions](drafts/201904-dfw-hackathon/agri-schema.ttl), linked 
to [sio:association](http://semanticscience.org/resource/SIO_000897))

### Markers for proposed new types and MIREOT-style importing

Types marked as `agri:AgriSchemasImported***` will automatically imported following the [MIREOT methodology][10]. See [agri-schema definitions](agri-schema.ttl).

[10]: https://content.iospress.com/articles/applied-ontology/ao087


## Relevant links

  * **==> [Working doc for schemas/ontologies](https://docs.google.com/document/d/15yMoJDvVEE-mDQgIUY-l1foTb35Qp_qsMIgReyP5VoQ/edit)**
  
  * [Working doc for the April 2019 hackathon](https://docs.google.com/document/d/1xzUyJMfBL7Prq8Whgp81ktoLLMisC5_3BfdZdEHO8Lg/edit#) for the hackathon
  
  * [Document by Rob Daves about data publication in DFW](https://docs.google.com/document/d/1ZEN3lHnzVIBshnLspH8ZTq4eVu2pu4JQDayhqr1qdNM/edit#)
  
  * [COPO Template for Field Trials](https://docs.google.com/spreadsheets/d/1vb0UyEFSyXVoxPG-egrMyw6K8SfL6MMDccgWYaHuGwM/edit?usp=sharing)

