# Modelling legal patents to describe biotechnologies

In this folder, you find a provisional first draft to describe patents and link them to relevant life science entities, such as genes.

This comes from some work we're doing in KnetMiner and everything should be considered in very experimental state. This is a [raw file we used as example](patent-data-example.csv).

## How to go from RDF to Labelled Property Graphs

The core of the example is this [RDF/Turtle file](example.ttl) ([Turtle tutorial][R2P10], [extended Turtle tutorial][R2P20]). We start from RDF, since, as of today, this is the only reliable standard for graph-like data and much of the schemas and ontologies we used are based on it.

We have converted the example to a JSON format that is suitable to be loaded into a graph database, ie, a representation in the form of Labelled Property Graph (LPG), which is the data model supported by Neo4j and which is similar to the RDF data model.

The [LPG flavour](example-knetminer.json) is here. There are a few rules that we have followed for the conversion, which we still have to finalise:

* namespaces: types like `schema:name` or `bioschema:Gene` are shortened straight to `name`, `Gene`, when the shorten name has no significant ambiguity and we know how to reconstruct the long version (ie, we can use an ordered list of preferred namespaces)

* names: types like `patent:applicationKind` are kept with their namespace prefix, since their short name is too ambiguous to be reliable, ie, what is `applicationKind`, what do you mean, 'application'? patent application? Software application?

* The `agrischema:` namespace is, as usually, for new types being proposed by the AgriSchemas project

* Similarly, we use namespaces for the most common schemas of reference in the AgriSchemas project: BioSchemas, schema.org. For patents, we have tried to the [EPO Patent Ontology too][R2P30].

* Types marked with the `knetminer:` namespaces are about KnetMiner-specific things, which we need to model in a schema file later (or to generalise to schemas like AgriSchemas).

* Other modelling choices are described in the [Turtle file](example.ttl)

* The final JSON/LPG file has been written passing through an intermediate [JSON-LD conversion](example.json). [JSON-LD Primer](R2P40)


[R2P10]: https://www.w3.org/2007/02/turtle/primer
[R2P20]: https://linkeddata.github.io/rdflib.js/Documentation/turtle-intro.html
[R2P30]: https://data.epo.org/linked-data/documentation/patent-ontology-overview
[R2P40]: https://docs.neuroweb.ai/knowledge-mining/knowledge-mining-kit/json-ld-tutorial
