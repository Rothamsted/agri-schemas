# Searching studies in GXA with full-text searches

## Getting study details

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

SELECT ?study ?acc ?title ?description ?taxId ?gxaAnalysis ?aeTech
WHERE {
	?study a bioschema:Study ;
		schema:identifier ?acc;
		dc:title ?title ;
		schema:description ?description;
		bioschema:studyProcess ?design.

	# FILTER ( ?acc IN ( ?paramAccs ) ).

	# TAX ID	
	#
	?specie schema:subjectOf ?study;
		bioschema:taxonomicRange ?taxon
	.
	BIND ( REPLACE ( STR ( ?taxon ), "http://purl.bioontology.org/ontology/NCBITAXON/", "" ) AS ?taxId )

	
	# Tech and Analysis type
	#
	?design schema:additionalProperty ?gxaAnalysis, ?aeTech.
	?gxaAnalysis schema:propertyID "gxaAnalysisType".
	?aeTech schema:propertyID "aeTechnologyType".
}
```

## Querying the most relevant text fields

```sparql
TODO
```