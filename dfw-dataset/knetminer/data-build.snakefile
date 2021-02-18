import os, glob
from etltools import sparqlmap
from etltools.utils import logger_config

log = logger_config ( __name__ )

KNET_RDF_DIR = os.getenv ( "KNET_RDF_DIR" )
ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TOOLS = os.getenv ( "ETL_TOOLS" )
etl_lib_path = ETL_TOOLS + "/lib/etltools/"
JENA_HOME = os.getenv ( "JENA_HOME" )

TDB_DIR = ETL_OUT + "tmp/tdb"
MAPPING_OUT = ETL_OUT + "/rdf/knetminer-mapping.nt"
	

rule all_mappings:
	input:
		TDB_DIR
	output:
		MAPPING_OUT
	message:
		"Generating the RDF mappings"
	run:
		sparql_vars = { 'SRC_NAMESPACE': 'bk:' }
		sparqlmap.map_from_files (
			[ etl_lib_path + "/map-rules", 
			  etl_lib_path + "/map-rules/schema-org" ],
			input[0], output[0], sparql_vars
		)
	

rdf_inputs  = [ "../agri-schema.ttl" ] \
  + glob.glob ( KNET_RDF_DIR + "/ontologies/*.*" ) \
  + glob.glob ( KNET_RDF_DIR + "/ontologies/ext/*.*" ) \
  + glob.glob ( KNET_RDF_DIR + "/*.*" )

rule generate_tdb:
  input:
  	rdf_inputs
  output:
    directory ( TDB_DIR )
	message:
		"Generating Working TDB '%s'" %  TDB_DIR
	run:
		print ( "Re-downloading BioKNO mappings" )
		shell ( "wget 'https://raw.githubusercontent.com/Rothamsted/bioknet-onto/master/bk_mappings.ttl' -O '" + KNET_RDF_DIR + "/ontologies/bk_mappings.ttl'" )
		shell ( "'" + JENA_HOME + "/bin/tdbloader' --loc={output} {input}" )

