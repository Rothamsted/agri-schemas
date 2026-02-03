# Searching GXA conditions with full-text searches

These queries works under Virtuoso, using their custom pseudo-predicate `bif:contains`. 

I didn't need any setup for this, however, I'm not sure it would perform well on large datasets.

Since the expression conditions might have ontology terms attaches, the quickest way to search for both is sending two queries (`bif:contains` has many limitations with UNION and OPTIONAL).

First, search by condition label:

```sparql
PREFIX bk: <http://knetminer.org/data/rdf/terms/biokno/>
PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
PREFIX bkg: <http://knetminer.org/data/rdf/resources/graphs/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX agri: <http://agrischemas.org/>
PREFIX bioschema: <https://bioschemas.org/>
PREFIX schema: <https://schema.org/>

SELECT ?condition ?condLabel ?condTerm ?condTermAcc ?condTermLabel
WHERE {
  ?condition a agri:StudyFactor ;
             schema:name ?condLabel .
  ?condLabel bif:contains "'disease' OR 'resistance'" .
  OPTIONAL {
    ?condition dc:type ?condTerm .
    ?condTerm schema:identifier ?condTermAcc ;
              schema:name ?condTermLabel .
  }
}
```

Next, merge what you can find through the annotating ontology term label:

```sparql
SELECT ?condition ?condLabel ?condTerm ?condTermAcc ?condTermLabel
WHERE {
  ?condition a agri:StudyFactor ;
             schema:name ?condLabel ;
             dc:type ?condTerm .
  ?condTerm schema:identifier ?condTermAcc ;
            schema:name ?condTermLabel .
  ?condTermLabel bif:contains "'disease' OR 'resistance'" .
}
```

Obviously, sending two queries is not a problem if you're doing it programmatically.