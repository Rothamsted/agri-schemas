import os, glob
from etltools import sparqlmap
from etltools.utils import logger_config

log = logger_config ( __name__ )

# The output from the rres pipeline
KNET_DATASET_DIR = os.getenv ( "KNET_DATASET_DIR" )
ETL_TMP = os.getenv ( "ETL_TMP" )

TDB_DIR = TMP_DIR + "agrischema-tdb"
 

rule update_tdb:
	input:
		ETL_TMP + "/tdb" # Produced by the RRes pipeline
	output:
	  directory ( TDB_DIR ) # We're adding our stuff and working with this
	shell:
	  f"""
	  /bin/cp -R -v "{{input}}" "{{output}}"
	  
	  # Load additional ontologies
	  "{JENA_HOME}/bin/tdbloader" --loc="{{output}}" "{KNET_DATASET_DIR}/ontologies/ext/*.*" ../../../agri-schema.ttl 
	  """
