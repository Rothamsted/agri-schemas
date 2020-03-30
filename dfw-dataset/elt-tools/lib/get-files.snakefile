import os, sys

"""
  This typically requires the --configfile parameter, else the get-files.yaml is used
"""

# configfile: "get-files.yaml"

import get_files_utils as mycfg
mycfg.init_config ( config )

rule get_all_files:
	input: mycfg.OUT_FILES

rule get_file:
	output:
		mycfg.TARGET_DIR + "/{out}"
	params:
		label = lambda wc: mycfg.INPUTS [ wc.out ] [ "label" ],
		url = lambda wc: mycfg.INPUTS [ wc.out ] [ "url" ]
	run:
		print ( "--- COPYING '%s'" % params [ "label" ] )
		shell ( "wget \"{params.url}\" -O \"{output}\"" )

rule clean:
	run:
		print ( "\n\tCleaning \"%s\"" % mycfg.TARGET_DIR )
		shell ( "rm -Rf \"%s\"" % mycfg.TARGET_DIR )
