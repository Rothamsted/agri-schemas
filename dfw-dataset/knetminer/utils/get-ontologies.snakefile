import os, sys

ELT_OUT = os.getenv ( "ELT_OUT" )
if not ELT_OUT:
	print ( "\n\tERROR: ELT_OUT undefined, Initialise the environment with some ***-env.sh\n" )
	sys.exit ( 1 )

configfile: "get-ontologies-cfg.yaml"

INPUTS = config [ "files" ]
TARGET_DIR = f"{ELT_OUT}/knetminer/ontologies"
OUT_FILES = INPUTS.keys ()

rule all:
	input:
		expand ( TARGET_DIR + "/{out}", out = OUT_FILES )

rule get_file:
	output:
		TARGET_DIR + "/{out}"
	params:
		label = lambda wc: INPUTS [ wc.out ] [ "label" ],
		url = lambda wc: INPUTS [ wc.out ] [ "url" ]
	run:
		print ( "--- COPYING '%s'" % params [ "label" ] )
		shell ( "wget \"{params.url}\" -O \"{output}\"" )

rule clean:
	run:
		print ( "\n\tCleaning \"%s\"" % TARGET_DIR )
		shell ( "rm -Rf \"%s\"" % TARGET_DIR )
