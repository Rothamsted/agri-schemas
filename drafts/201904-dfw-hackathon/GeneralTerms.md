# General approach

* No more than 10 namespaces we reuse directly, all the rest needs to have local defs
* for code-based URIs (eg, SIO_XXX), we need human-readable counterparts

* schema
* dc
* rdfs
* bioschemas
* skos
* prov
* annotation

* avoid to define inverse properties of existing properties, just use the available one, in the 
  available direction.

* TODO: Marking new proposals
* TODO: MIRO-like procedure for imports

# Concept (schema:DefinedTerm)

Used to subclass vocabulary terms, tags, categories and alike.
An ontology term (eg, GO_XXX) might fall into this, if used as a vocabulary term.

Maps to: skos:Concept, schema:DefinedTerm, TODO

Properties to be used to annotate an entity with a concept:

* schema:subjectOf, rdfs:seeAlso 


# name, altName, label, description, accession
  might need qualified version (eg, source)



# Attributes with qualifiers


# Standard way for reification
  proposal: n-ary relations, align better with PG, allows for reuse of existing relations


# Provenance
  * source
  * evidence


# Use Cases
  * KnetMiner biological pathway
    * includes proteins, protein complexes, genes, provenance, reactions, gene encoding
    * includes concept terms
    * include reification
  * Concept Scheme from GO
  * Publication
  


