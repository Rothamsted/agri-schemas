

# AgriSchema queries related to GXA

## Select genes

```sql
PREFIX bk: <http://knetminer.org/data/rdf/terms/biokno/>
PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
PREFIX bka: <http://knetminer.org/data/rdf/terms/biokno/attributes/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX agri: <http://agrischemas.org/>
PREFIX bioschema: <http://bioschemas.org/>
PREFIX schema: <http://schema.org/>

SELECT ?gene ?geneAcc ?condLabel ?studyTitle ?study ?condTerm 
{
?gene a bk:Gene;
  dcterms:identifier ?geneAcc.

FILTER ( UCASE (?geneAcc) IN ( 
  'TRAESCS2D02G242700','TRAESCSU02G073600','TRAESCS7D02G050400',
  'TRAESCS6D02G393900','TRAESCS7D02G503700','TRAESCS7D02G431500',
  'TRAESCS1D02G090100','TRAESCS1D02G156000','TRAESCS2B02G046700',
  'TRAESCS4A02G318000','TRAESCS1A02G443400','TRAESCS7D02G241300',
  'TRAESCS6D02G107700','TRAESCS5D02G247200'
))  

?gene bioschema:expressedIn ?condition.
  
?expStatement a rdfs:Statement;
  rdf:subject ?gene;
  rdf:predicate bioschema:expressedIn;
  rdf:object ?condition;
  agri:score ?score;
  agri:evidence ?study.
                
?condition schema:prefName ?condLabel.
OPTIONAL { ?condition schema:additionalType ?condTerm. }
  
?study 
  dc:title ?studyTitle;
}
ORDER BY ?study ?gene
```


## Combining genes, GXA experiments and Knet pubs

```sql
PREFIX bk: <http://knetminer.org/data/rdf/terms/biokno/>
PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
PREFIX bka: <http://knetminer.org/data/rdf/terms/biokno/attributes/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX agri: <http://agrischemas.org/>
PREFIX bioschema: <http://bioschemas.org/>
PREFIX schema: <http://schema.org/>

SELECT ?gene ?geneAcc ?condLabel ?studyTitle ?study ?pub ?pubTitle ?pubYear ?condTerm 
{
	?gene a bk:Gene;
		dcterms:identifier ?geneAcc.
		
	?gene bioschema:expressedIn ?condition.
		
	?expStatement a rdfs:Statement;
		rdf:subject ?gene;
		rdf:predicate bioschema:expressedIn;
		rdf:object ?condition;
		agri:score ?score;
		agri:evidence ?study.
									
	?gene bk:occ_in ?pub.
		
	?pub a bk:Publication;
		bka:AbstractHeader ?pubTitle.
	OPTIONAL { ?pub bka:YEAR ?pubYear }
			
	?condition schema:prefName ?condLabel.
	OPTIONAL { ?condition schema:additionalType ?condTerm. }
		
	?study 
		dc:title ?studyTitle;
}
ORDER BY ?study ?gene
```



# Some tests with the GXA SPARQL endopoint

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
	?experiment inTaxon:/rdfs:label 'Triticum aestivum'.
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