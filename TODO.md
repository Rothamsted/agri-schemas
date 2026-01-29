# AgriSchemas TODOs

*Last updated: 2026-01-26*

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
* ETL issues from real data
	* E-GEOD-19700: we don't support time points like 06:00, 12:00 etc (damn!)
		* This shows how scraping their data is shitty: let's contact them again and ask to 
		collaborate to an API
		* See the similar cases below: are there damn rules to know all the possible variants?
	* E-GEOD-50526: similar problem, with the variant 'at 24 hours post infection'
	* E-GEOD-19603: similar, "2 hours at 37 C"
	* Others: E-TABM-51 E-GEOD-21786 E-GEOD-18982 E-GEOD-18985 E-MTAB-4222 E-MTAB-8557 E-GEOD-15689 E-MTAB-8021 E-GEOD-4733 E-MTAB-4308 E-GEOD-32193 E-MEXP-2229 E-GEOD-34476 E-MEXP-1863 E-TABM-919 E-GEOD-29589 E-GEOD-13739 E-MTAB-4782 E-GEOD-29657

