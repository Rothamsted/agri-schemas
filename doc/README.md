# Modelling Agri-Schemas

This is a project to model linked data schemas (ie, lightweight ontologies for the fields of agriculture, food, agri-business, plant biology.

The work leverages mainly [schema.org](https://schema.org/) and [bioschemas](https://bioschemas.org/). As in those projects, we aim at very simple and practical modelling, which can be useful to share data in an interoperable way, especially by means of APIs and annotated web pages.

The work was born within the [Design Future Wheat](https://designingfuturewheat.org.uk/) project, and for the moment it's focused on the use cases dealt with in it. In fact, so far we have been building our schemas starting from well known use cases within crop improvement research. There have been two DFW hackathons where we have done most of the work so far.

## Use cases

This work has started with a first DFW hackathon in 2018, where we first [outlined the possible types](https://docs.google.com/document/d/15yMoJDvVEE-mDQgIUY-l1foTb35Qp_qsMIgReyP5VoQ/edit) (ie, classes, properties/relations) that we might need in DFW-relevant data.

Leveraging that, we have started considering use cases from real data, and we have started modelling them using existing schemas. At the same time, we have started to [propose new types](agri-schema.ttl) as needed.

These are the use cases considered:

  * [Molecular Biology, pathways/genes/proteins](biomol-use-case.ttl) (from Knetminer)
  * [Molecular Biology, ontology terms](ontology-use-case.ttl) (from Knetminer)
  * [Semantic annotations](text-mining-use-case) (ex, text mining annotations)
  * [Molecular Biology, host-pathogen interactions](phi-base-use-case.ttl) (PHI-Base)
  * Dataset description, TODO (based on `bioschema:Dataset`, but CKAN might need DCAT, VoID is also worth to consider)
  * Field trials
    * [MIAPPE and ISA-Tab for phenotyping](miappe-use-case)
    * [AHDB](ahdb-use-case.md)
  * Links between [field trials, cultivars and genes](trials-genes.md)
    * Includes the [EBI Gene Expression Atlas use case](ebi-gxa-use-case/README.md)
  * [Patents linked to life science entities](patents/README.md)
  * [Weather conditions and forecasts](weather-use-case.md)

## Modelling principles
[Some notes](modelling-principles.md) on general criteria adopted to outline the use case models above.

## References
[A collection of references](references.md) and links to various similar projects hackathons, schemas, etc.
