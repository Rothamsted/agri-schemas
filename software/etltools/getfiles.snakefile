import os, sys

"""
  This typically requires the --configfile parameter, else the getfiles.yaml is used
"""

# configfile: "getfiles.yaml"

import getfilescfg as cfg
cfg.init_config ( config )

rule get_all_files:
	input: cfg.OUT_FILES

rule get_file:
	output:
		cfg.TARGET_DIR + "/{out}"
	params:
		label = lambda wc: cfg.INPUTS [ wc.out ] [ "label" ],
		url = lambda wc: cfg.INPUTS [ wc.out ] [ "url" ]
	run:
		print ( "--- GETTING '%s'" % params [ "label" ] )
		shell ( "wget \"{params.url}\" -O \"{output}\"" )

rule clean_files:
	run:
		print ( "\n\tCleaning \"%s\"" % cfg.TARGET_DIR )
		shell ( "rm -Rf \"%s\"" % cfg.TARGET_DIR )
