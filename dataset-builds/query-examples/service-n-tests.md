# Useful queries for AgriSchemas datasets

## Describe a resource with a couple of levels

```sql
prefix bkr: <http://knetminer.org/data/rdf/resources/>

construct {
  ?s ?p ?o.
  ?o ?p1 ?o1.
  ?o1 ?p2 ?o2.
}
where {
  VALUES (?s) { ( bkr:exp_E-ATMX-20 ) }
  ?s ?p ?o.

  OPTIONAL { 
    ?o ?p1 ?o1 
    OPTIONAL { ?o1 ?p2 ?o2  }
  }
} LIMIT 10000
```

## Are we still using the damn blank nodes?

(Works with Virtuoso)

```sql
PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
PREFIX agri: <http://agrischemas.org/>
PREFIX bioschema: <https://bioschemas.org/>
PREFIX schema: <http://schema.org/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX efo: <http://www.ebi.ac.uk/efo/>

construct {
?b ?p ?o .
?s ?rp ?b
}
where {
  GRAPH <http://knetminer.org/data/rdf/resources/graphs/gxaAgriSchemas> {
  { ?b ?p ?o FILTER ( STRSTARTS (STR(?b), "nodeID:")) }
  union {?s ?rp ?b FILTER ( STRSTARTS (STR(?b), "nodeID:")) }  
  }
} LIMIT 10000
```