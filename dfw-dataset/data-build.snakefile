import os, sys, glob
from etltools import sparqlmap
from etltools.utils import logger_config
import io

log = logger_config ( __name__ )

ETL_OUT = os.getenv ( "ETL_OUT" )

include:
  knetminer/data-build.snakefile
  gxa/data-build.snakefile

rule all:
	output:
		glob.glob ( ETL_OUT + "rdf/*.*" )
	message:
		"Aggregating all the files"
	
rule clean:
	run:
		print ( "\n\tCleaning \"%s\"" % ETL_OUT )
		shell ( "rm -Rf \"%s\"" % ETL_OUT )
