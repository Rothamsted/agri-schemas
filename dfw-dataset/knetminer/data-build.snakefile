import os, glob
from etltools import sparqlmap
from etltools.utils import logger_config

log = logger_config ( __name__ )

# The output from the rres pipeline
ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TMP = os.getenv ( "ETL_TMP" )
TDB_DIR = ETL_TMP + "/agrischema-tdb"
 
JENA_HOME = os.getenv ( "JENA_HOME" )

update_tdb_done_flag_path = f"{ETL_TMP}/update_tdb.done-flag"


rule update_tdb:
	input:
		TDB_DIR,
		f"{ETL_OUT}/ontologies/ext/agri-schema.ttl"		
	message:
		"Extending Knetminer TDB with additional ontologies"
	output:
	  update_tdb_done_flag_path # No other way for input = out 
	shell:
	  f"""
	  '{JENA_HOME}/bin/tdbloader' --loc='{TDB_DIR}' '{ETL_OUT}/ontologies/ext/'*.*
	  echo "1" >'{{output}}'
	  """


rule clone_tdb:
	input:
		ETL_TMP + "/tdb", # Produced by the RRes pipeline
		f"{ETL_OUT}/ontologies/ext/agri-schema.ttl" # binds it to update_ontologies		
	message:
		"Working on a Knetminer TDB copy"
	output:
	  directory ( TDB_DIR ) # We're adding our stuff and working with this
	shell:
	  f"/bin/cp -R -v '{{input[0]}}' '{{output}}'"


rule update_ontologies:
	input:
		"../../agri-schema.ttl"
	output:
		f"{ETL_OUT}/ontologies/ext/agri-schema.ttl"
	message:
		"Deploying agri-schema ontology"
	shell:
		"/bin/cp -R -v '{input}' '{output}'"
