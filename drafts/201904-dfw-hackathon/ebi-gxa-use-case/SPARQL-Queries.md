
## Inspecting experiments about Triticum

```sql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>

PREFIX atlasterms: <http://rdf.ebi.ac.uk/terms/expressionatlas/>
PREFIX atlas: <http://rdf.ebi.ac.uk/resource/expressionatlas/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX inTaxon: <http://purl.obolibrary.org/obo/RO_0002162>


SELECT ?gene
FROM <http://rdf.ebi.ac.uk/dataset/expressionatlas>
WHERE {
    ?experiment a/rdfs:subClassOf* atlasterms:Experiment.
	?experiment inTaxon:/rdfs:label "Triticum aestivum".
	?experiment atlasterms:hasPart ?analysis .
	?analysis atlasterms:hasOutput ?value . 
	?analysis atlasterms:hasFactorValue ?factor .  
	?value atlasterms:refersTo ?gene . 
}
```

## Inspecting Genes

```sql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dbpedia2: <http://dbpedia.org/property/>
PREFIX dbpedia: <http://dbpedia.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ensembl: <http://rdf.ebi.ac.uk/resource/ensembl/>

DESCRIBE ?uri
{
  ?uri dc:identifier ?id.
  
  VALUES (?id) {
(ensembl:TraesCS3B02G007400)
(ensembl:TraesCS2A02G025700)
(ensembl:TraesCS2D02G530600)
(ensembl:TraesCS2A02G527700)
(ensembl:TraesCS2B02G558400)
(ensembl:TraesCS2B02G038700)
(ensembl:TraesCS3B02G257900)
(ensembl:TraesCS3A02G226600)
(ensembl:TraesCS3D02G224600)
(ensembl:TraesCS3D02G468400)
(ensembl:TraesCS3B02G280700)	
  }
}
```