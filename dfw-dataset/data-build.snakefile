import os, sys, glob
from etltools import sparulmap

KNET_RDF_DIR = os.getenv ( "KNET_RDF_DIR" )
ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TOOLS = os.getenv ( "ETL_TOOLS" )

etl_lib_path = ETL_TOOLS + "/lib/etltools/"

JENA_HOME = os.getenv ( "JENA_HOME" )

TDB_DIR = ETL_OUT + "/tdb"
MAPPING_OUT = ETL_OUT + "/knetminer-mapping.ttl"

rule all:
	input:
		TDB_DIR
	output:
		MAPPING_OUT
	message:
		"Generating the mappings"
	run:
		sparql_vars = { 'TARGET_NAMESPACE': 'schema:' }
		sparulmap.map_from_files (
			[ etl_lib_path + "/map-rules", 
			  etl_lib_path + "/map-rules/schema-org" ],
			input[0], "ex:mappedGraph", output[0], sparql_vars
		)
	

all_inputs  = [ "../agri-schema.ttl" ] \
  + glob.glob ( KNET_RDF_DIR + "/ontologies/*.*" ) \
  + glob.glob ( KNET_RDF_DIR + "/ontologies/ext/*.*" ) \
  + glob.glob ( KNET_RDF_DIR + "/*.*" )

rule generate_tdb:
  input:
  	all_inputs
  output:
    directory ( TDB_DIR )
	message:
		"Generating Test TDB"
	shell:
		f"'{JENA_HOME}/bin/tdbloader'" + " --loc={output} {input}"


rule clean:
	run:
		for path in [ KNET_RDF, ETL_OUT ]:
			print ( "\n\tCleaning \"%s\"" % path )
			shell ( "rm -Rf \"%s\"" % path )
