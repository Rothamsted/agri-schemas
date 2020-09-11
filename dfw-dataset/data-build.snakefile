import os, sys, glob
from etltools import sparqlmap

KNET_RDF_DIR = os.getenv ( "KNET_RDF_DIR" )
ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TOOLS = os.getenv ( "ETL_TOOLS" )

etl_lib_path = ETL_TOOLS + "/lib/etltools/"

JENA_HOME = os.getenv ( "JENA_HOME" )

TDB_DIR = ETL_OUT + "/tdb"
MAPPING_OUT = ETL_OUT + "/knetminer-mapping.nt"

rule all:
	input:
		TDB_DIR
	output:
		MAPPING_OUT
	message:
		"Generating the mappings"
	run:
		sparql_vars = { 'SRC_NAMESPACE': 'bk:' }
		sparqlmap.map_from_files (
			[ etl_lib_path + "/map-rules", 
			  etl_lib_path + "/map-rules/schema-org" ],
			input[0], output[0], sparql_vars
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
		"Generating Test TDB '%s'" %  TDB_DIR
	run:
		print ( "Re-downloading BioKNO mappings" )
		shell ( "wget 'https://raw.githubusercontent.com/Rothamsted/bioknet-onto/master/bk_mappings.ttl' -O '" + KNET_RDF_DIR + "/ontologies/bk_mappings.ttl'" )
		shell ( "'" + JENA_HOME + "/bin/tdbloader' --loc={output} {input}" )


rule clean:
	run:
		for path in [ KNET_RDF, ETL_OUT ]:
			print ( "\n\tCleaning \"%s\"" % path )
			shell ( "rm -Rf \"%s\"" % path )
