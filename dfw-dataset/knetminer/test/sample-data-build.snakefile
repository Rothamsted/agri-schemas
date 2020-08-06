import os, sys
from etltools import sparulmap
import etltools.getfilescfg as onto_cfg

ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TOOLS = os.getenv ( "ETL_TOOLS" )

etl_lib_path = ETL_TOOLS + "/lib/etltools/"

#configfile: "../../snake-config.yaml"
include: etl_lib_path + "/getfiles.snakefile"

ODX2RDF = os.getenv ( "ODX2RDF" )
JENA_HOME = os.getenv ( "JENA_HOME" )

onto_cfg.init_config ( config )

TEST_OXL = ODX2RDF + "/examples/text_mining.oxl"
TEST_RDF = ETL_OUT + "/test/knetminer-sample.ttl"
TEST_TDB = ETL_OUT + "/test/test-tdb"
MAPPING_OUT = ETL_OUT + "/test/knetminer-mapping-test-out.ttl"

rule all:
	input:
		TEST_TDB
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
	
rule generate_tdb:
  input: onto_cfg.OUT_FILES + [ TEST_RDF, "../../../agri-schema.ttl" ]
	output: directory ( TEST_TDB )
	message:
		"Generating Test TDB"
	shell:
		f"'{JENA_HOME}/bin/tdbloader'" + " --loc={output} {input}"


rule generate_rdf:
	input:
		TEST_OXL
	output:
		TEST_RDF
	message:
		"Generating RDF from the test OXL"
	shell:
		f"'{ODX2RDF}/odx2rdf.sh'" + " {input} {output}"


rule clean:
	run:
		print ( "\n\tCleaning \"%s\"" % ETL_OUT )
		shell ( "rm -Rf \"%s\"" % ETL_OUT )
