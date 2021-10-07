import os, sys
import glob
from etltools import sparqlmap
from etltools.utils import download_files

ETL_OUT = os.getenv ( "ETL_OUT" )
AG_LIB = os.getenv ( "AG_LIB" )
etl_tools_path = AG_LIB + "/etltools"
JENA_HOME = os.getenv ( "JENA_HOME" )
OXL2NEO_HOME = os.getenv ( "OXL2NEO_HOME" )

TEST_RDF_URL = "https://github.com/Rothamsted/knetminer-backend/blob/master/test-data-server/src/main/resources/poaceae-sample.ttl.bz2?raw=true"
TEST_RDF = ETL_OUT + "/test/knetminer-sample.ttl.bz2"
TEST_TDB = ETL_OUT + "/test/test-tdb"
MAPPING_OUT = ETL_OUT + "/test/knetminer-mapping-test-out.nt"

ontos_dir = ETL_OUT + "/test/ontologies"


rule all:
	input:
		TEST_TDB
	output:
		MAPPING_OUT
	message:
		"Generating the mappings"
	run:
		sparql_vars = { 'SRC_NAMESPACE': 'bk:' }
		sparqlmap.map_from_files (
			[ etl_tools_path + "/map-rules", 
			  etl_tools_path + "/map-rules/schema-org" ],
			input[0], output[0], sparql_vars
		)
	
rule generate_tdb:
	input:
	  ontos_dir,
		"../../../agri-schema.ttl",
		TEST_RDF
	output:
		directory ( TEST_TDB )
	message:
		"Generating Test TDB"
	shell:
		f"'{JENA_HOME}/bin/tdbloader' --loc={{output}} {ontos_dir}/*.* {ontos_dir}/ext/*.* ../../../agri-schema.ttl {TEST_RDF}"

rule download_rdf:
	output:
		TEST_RDF
	message:
		"Getting Poaceae Sample Dataset RDF"
	shell:
		f'wget -O "{{output}}" "{TEST_RDF_URL}"' 

rule download_ontos:
	output:
		directory ( ontos_dir )
	message:
		"Getting Ontologies"
	run:
		shell ( f'mkdir -p "{ontos_dir}"' )
		shell ( f'"{OXL2NEO_HOME}/get_ontologies.sh" "{{output}}"' )


rule clean:
	run:
		print ( "\n\tCleaning \"%s\"" % ETL_OUT )
		shell ( "rm -Rf \"%s\"" % ETL_OUT )
