import os, glob
from etltools import sparqlmap
from etltools.utils import logger_config

log = logger_config ( __name__ )

# The output from the rres pipeline
AG_LIB = os.getenv ( "AG_LIB" )
etl_tools_path = AG_LIB + "/etltools"

ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TMP = os.getenv ( "ETL_TMP" )
TDB_DIR = ETL_TMP + "/agrischema-tdb"

JENA_HOME = os.getenv ( "JENA_HOME" )

update_tdb_done_flag_path = f"{ETL_TMP}/update_tdb.done-flag"

mapping_out_path = ETL_OUT + "/agrischemas-map.nt" 


rule compress_map:
	message:
		"Compressing the resulting RDF"
	input:
		mapping_out_path
	output:
		mapping_out_path + ".bz2"
	shell:
		"bzip2 '{input}'; sleep 10"


rule map:
	message:
		"Creating agri-schemas Mappings"
	input:
		TDB_DIR,
		update_tdb_done_flag_path
	output:
		temp ( mapping_out_path )
	run:
		sparqlmap.map_from_files (
			rule_paths = [ etl_tools_path + "/map-rules", etl_tools_path + "/map-rules/schema-org" ],
			tdb_path = input[0],
			dump_file_path = output[0], 
			sparql_vars = { 'SRC_NAMESPACE': 'bk:' }
		)


rule update_tdb:
	message:
		"Extending Knetminer TDB with additional ontologies"
	input:
		TDB_DIR,
		f"{ETL_OUT}/ontologies/ext/agri-schema.ttl"		
	output:
	  update_tdb_done_flag_path # No other way for input = out 
	shell:
	  f"""
	  '{JENA_HOME}/bin/tdb2.tdbloader' --loc='{{input[0]}}' '{ETL_OUT}/ontologies/ext/'*.*
	  echo 1 >'{{output}}'
	  """


rule clone_tdb:
	message:
		"Working on a Knetminer TDB copy"
	input:
		ETL_TMP + "/tdb", # Produced by the RRes pipeline
	output:
	  directory ( TDB_DIR ) # We're adding our stuff and working with this
	shell:
	  f"/bin/cp -R -v '{{input[0]}}' '{{output}}'"


rule update_ontologies:
	message:
		"Deploying agri-schema ontology"
	input:
		"../../agri-schema.ttl"
	output:
		f"{ETL_OUT}/ontologies/ext/agri-schema.ttl"
	shell:
		# Pause required by NFS latency
		"/bin/cp -R -v '{input}' '{output}'; sleep 10"
