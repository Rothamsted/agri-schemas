# AgriSchemas TODOs

*Last updated: 2026-01-15*

## Fixes in Existing files

* dc:title => dcterms:title

## Alignments to Bioschemas and schema.org

* Publications use schema:name for title, not headline (see their profile).

## GXA RDF Converter
* 2026-01-17: Review against the MIAPPE use case. Eg, study has dc:title on the converter, the bioschema profile wants schema:name.
* ETL
	* Run it against all the experiments
	* static files copy to out, eg, `.venv/lib/python*/site-packages/agrischemas/ebigxa/gxa-rdf-defaults.ttl`
	* ontology files download
	* Virtuoso scripts (or Fuseki? Consider we need full text searches)
  * databuild.sh: argument parsing, env-id
	* Add further organisms

