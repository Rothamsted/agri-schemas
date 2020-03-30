import os, sys


if not os.getenv ( "DFW_ELT" ):
	print ( "\n\tERROR: DFW_ELT undefined, this script should be run by sample-data-test.sh\n" )
	sys.exit ( 1 )

ELT_OUT = os.getenv ( "ELT_OUT" )
ELT_TOOLS = os.getenv ( "ELT_TOOLS" )

sys.path.append ( ELT_TOOLS + "/lib" )
import get_files_utils as mycfg

configfile: "../../snake-config.yaml"
include: ELT_TOOLS + "/lib/get-files.snakefile"

ODX2RDF = os.getenv ( "ODX2RDF" )
JENA_HOME = os.getenv ( "JENA_HOME" )

mycfg.init_config ( config )

TEST_OXL = ODX2RDF + "/examples/text_mining.oxl"
TEST_RDF = ELT_OUT + "/test/knetminer-sample.ttl"
TEST_TDB = os.getenv ( "TEST_TDB" )
MAPPING_OUT = ELT_OUT + "/test/knetminer-mapping-test-out.ttl"

rule all:
	input:
		TEST_TDB
	output:
		MAPPING_OUT
	message:
		"Generating the mappings"
	shell:
		f"'{ELT_TOOLS}/sparul-mapping/sparul-mapping.sh'" 
		 + " {input} 'schema:' \"<$(ns agGraph)knetminer-sample>\" '{output}'"


rule generate_tdb:
  input: mycfg.OUT_FILES + [ TEST_RDF ]
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

